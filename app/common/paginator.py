from datetime import datetime
import math
from abc import ABC, abstractmethod
from uuid import UUID
from sqlmodel import SQLModel, select, desc, asc,func
from pydantic import BaseModel, PositiveInt
from sqlalchemy.sql.base import ExecutableOption
from sqlalchemy.sql.elements import SQLColumnExpression
from typing import Generic, Type, TypeVar, List, Optional, Tuple, Union, Literal
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.sql._typing import _ColumnExpressionArgument


T = TypeVar('T', bound=SQLModel)


SortChoice = Literal["asc", "desc"]

class PaginatorOrderBy(BaseModel):
    column: SQLColumnExpression #type: ignore
    choice: SortChoice

    model_config = {
        "arbitrary_types_allowed": True
    }

class PaginationSchema:
    def __init__(self, page: PositiveInt = 1, limit: PositiveInt = 10):
        self.page = page
        self.limit = limit


class CursorPaginationSchema:
    def __init__(
        self, 
        limit: PositiveInt = 50, 
        cursor: Optional[Union[UUID, datetime, int, str]] = None,
        direction: Literal["before", "after"] = "before"
    ):
        self.limit = limit
        self.cursor = cursor
        self.direction = direction



class PaginatorMeta(BaseModel):
    total: int
    per_page: int
    last_page: int
    current_page: int
    prev: Optional[int]
    next: Optional[int]


class PaginatorResult(BaseModel, Generic[T]):
    results: List[T]
    meta:  PaginatorMeta



class CursorPaginatorMeta(BaseModel):
    has_more: bool
    next_cursor: Optional[Union[UUID, datetime, int, str]]
    prev_cursor: Optional[Union[UUID, datetime, int, str]]
    count: int


class CursorPaginatorResult(BaseModel, Generic[T]):
    results: List[T]
    meta: CursorPaginatorMeta


class BasePaginator(ABC, Generic[T]):

    @abstractmethod
    async def apaginate(self, session: AsyncSession) -> PaginatorResult[T] | CursorPaginatorResult[T]:
        ...



class PageNumberPaginator(BasePaginator[T]):

    def __init__(self, *, model: Type[T], paginator_schema: PaginationSchema, whereclause: Optional[Tuple[Union[_ColumnExpressionArgument[bool], bool]]] = None, order_by: Optional[PaginatorOrderBy] = None, options: Optional[Tuple[ExecutableOption]] = None):
        self.model = model
        self.paginator_schema = paginator_schema

        self.whereclause = whereclause or ()


        self.options = options or ()
        
        self.order_by = order_by or PaginatorOrderBy(column=self.model.created_at, choice="desc") # type: ignore

    def get_offset(self) -> int:
        offset = (self.paginator_schema.page - 1) * self.paginator_schema.limit
        return offset

    async def apaginate(self, session: AsyncSession) -> PaginatorResult[T]:
        offset = self.get_offset()

        if self.order_by.choice == "desc":
            final_order_by = desc(self.order_by.column)
        else:
            final_order_by = asc(self.order_by.column)
    
        items: list[T] = (await session.exec(select(self.model).where(*self.whereclause).options(*self.options).offset(offset).limit(self.paginator_schema.limit).order_by(final_order_by))).all() # type: ignore
        
        total = (await session.exec(select(func.count(self.model.id).label("item_count")).where(*self.whereclause))).one() # type: ignore


        last_page = math.ceil(total / self.paginator_schema.limit)
        current_page = self.paginator_schema.page


        return PaginatorResult(
            results=items,
            meta= PaginatorMeta(
                total=total,
                last_page=last_page,
                current_page=current_page,
                per_page=self.paginator_schema.limit,
                prev=current_page - 1 if current_page > 1 else None,
                next=current_page + 1 if current_page < last_page else None
            )

        )
    

class CursorPaginator(BasePaginator[T]):
    """
    Cursor-based pagination for infinite scrolling and real-time feeds.
    
    Example usage:
        paginator = CursorPaginator(
            model=ConversationMessage,
            paginator_schema=CursorPaginationSchema(limit=50, cursor=some_id, direction="before"),
            whereclause=(ConversationMessage.conversation_id == conversation_id,),
            cursor_column=ConversationMessage.created_at,  # Column to use for cursor
            order_by=PaginatorOrderBy(column=ConversationMessage.created_at, choice="desc")
        )
    """

    def __init__(
        self, 
        *, 
        model: Type[T], 
        paginator_schema: CursorPaginationSchema,
        cursor_column: SQLColumnExpression,  # type: ignore # The column to use as cursor (usually created_at or id)
        whereclause: Optional[Tuple[Union[_ColumnExpressionArgument[bool], bool]]] = None, 
        order_by: Optional[PaginatorOrderBy] = None, 
        options: Optional[Tuple[ExecutableOption]] = None,
        reverse_results: bool = True  # Reverse results for chat-like display (oldest first)
    ):
        self.model = model
        self.paginator_schema = paginator_schema
        self.cursor_column = cursor_column
        self.whereclause = whereclause or ()
        self.options = options or ()
        self.order_by = order_by or PaginatorOrderBy(column=self.cursor_column, choice="desc")
        self.reverse_results = reverse_results

    async def apaginate(self, session: AsyncSession) -> CursorPaginatorResult[T]:
        # Build base query
        query = select(self.model).where(*self.whereclause).options(*self.options)
        
        # Apply cursor filter if provided
        if self.paginator_schema.cursor is not None:
            # Get the cursor value from the database
            cursor_value_query = select(self.cursor_column).where(
                self.model.id == self.paginator_schema.cursor
            ).limit(1)
            cursor_value = (await session.exec(cursor_value_query)).first()
            
            if cursor_value is not None:
                if self.paginator_schema.direction == "before":
                    # Get items before cursor (older)
                    if self.order_by.choice == "desc":
                        query = query.where(self.cursor_column < cursor_value)
                    else:
                        query = query.where(self.cursor_column > cursor_value)
                else:
                    # Get items after cursor (newer)
                    if self.order_by.choice == "desc":
                        query = query.where(self.cursor_column > cursor_value)
                    else:
                        query = query.where(self.cursor_column < cursor_value)
        
        # Apply ordering
        if self.order_by.choice == "desc":
            final_order_by = desc(self.order_by.column)
        else:
            final_order_by = asc(self.order_by.column)
        
        # Fetch limit + 1 to check if there are more items
        query = query.order_by(final_order_by).limit(self.paginator_schema.limit + 1)
        
        items: list[T] = (await session.exec(query)).all()  # type: ignore
        
        # Check if there are more items
        has_more = len(items) > self.paginator_schema.limit
        if has_more:
            items = items[:self.paginator_schema.limit]
        
        # Reverse for proper display order if needed (e.g., chat messages - oldest first)
        if self.reverse_results:
            items.reverse()
        
        # Determine next and previous cursors
        next_cursor = None
        prev_cursor = None
        
        if items:
            if self.reverse_results:
                # After reversing: first item is oldest, last is newest
                next_cursor = items[0].id if has_more else None  # Oldest item for "load more old"
                prev_cursor = items[-1].id  # Newest item for "load more new"
            else:
                # No reversing: maintain order
                next_cursor = items[-1].id if has_more else None
                prev_cursor = items[0].id if self.paginator_schema.cursor else None
        
        return CursorPaginatorResult(
            results=items,
            meta=CursorPaginatorMeta(
                has_more=has_more,
                next_cursor=next_cursor,
                prev_cursor=prev_cursor,
                count=len(items)
            )
        )