'use client';

import * as React from 'react';
import { useRouter } from 'next/navigation';
import {
  IconChevronDown,
  IconChevronLeft,
  IconChevronRight,
  IconChevronsLeft,
  IconChevronsRight,
  IconDotsVertical,
  IconLayoutColumns,
  IconFileText,
  IconFileCode,
} from '@tabler/icons-react';
import {
  ColumnDef,
  ColumnFiltersState,
  flexRender,
  getCoreRowModel,
  getFacetedRowModel,
  getFacetedUniqueValues,
  getFilteredRowModel,
  getSortedRowModel,
  SortingState,
  useReactTable,
  VisibilityState,
} from '@tanstack/react-table';
import { toast } from 'sonner';

import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Checkbox } from '@/components/ui/checkbox';
import {
  DropdownMenu,
  DropdownMenuCheckboxItem,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import type { ConversationsListView, ConversationSummaryView } from '@/lib/conversations';
import { buildConversationDownloadUrl } from '@/lib/conversations';

function formatDuration(seconds: number | null): string {
  if (!seconds) return '-';
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  const s = Math.floor(seconds % 60);
  if (h > 0) {
    return `${h}:${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
  }
  return `${m}:${s.toString().padStart(2, '0')}`;
}

function formatDateTime(dateString: string | null): string {
  if (!dateString) return '-';
  const date = new Date(dateString);
  return new Intl.DateTimeFormat('de-DE', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  }).format(date);
}

function truncateText(text: string | null, maxLength: number = 50): string {
  if (!text) return '-';
  if (text.length <= maxLength) return text;
  return text.substring(0, maxLength) + '...';
}

const columns: ColumnDef<ConversationSummaryView>[] = [
  {
    id: 'select',
    header: ({ table }) => (
      <div className="flex items-center justify-center">
        <Checkbox
          checked={
            table.getIsAllPageRowsSelected() ||
            (table.getIsSomePageRowsSelected() && 'indeterminate')
          }
          onCheckedChange={(value) => table.toggleAllPageRowsSelected(!!value)}
          aria-label="Alle auswählen"
        />
      </div>
    ),
    cell: ({ row }) => (
      <div className="flex items-center justify-center">
        <Checkbox
          checked={row.getIsSelected()}
          onCheckedChange={(value) => row.toggleSelected(!!value)}
          aria-label="Zeile auswählen"
        />
      </div>
    ),
    enableSorting: false,
    enableHiding: false,
  },
  {
    accessorKey: 'id',
    header: 'ID',
    cell: ({ row }) => {
      return (
        <Button
          variant="link"
          className="text-foreground h-auto w-fit px-0 text-left font-mono text-sm"
          onClick={() => {
            toast.info(`Detailansicht für Gespräch ${row.original.id} wird später implementiert`);
          }}
        >
          {row.original.id}
        </Button>
      );
    },
  },
  {
    accessorKey: 'startedAt',
    header: 'Start',
    cell: ({ row }) => {
      return <div className="text-sm">{formatDateTime(row.original.startedAt)}</div>;
    },
  },
  {
    accessorKey: 'endedAt',
    header: 'Ende',
    cell: ({ row }) => {
      return <div className="text-sm">{formatDateTime(row.original.endedAt)}</div>;
    },
  },
  {
    accessorKey: 'durationSeconds',
    header: 'Dauer',
    cell: ({ row }) => {
      return <div className="text-sm font-mono">{formatDuration(row.original.durationSeconds)}</div>;
    },
  },
  {
    accessorKey: 'turnCount',
    header: 'Züge',
    cell: ({ row }) => {
      return <div className="text-sm">{row.original.turnCount}</div>;
    },
  },
  {
    accessorKey: 'userPhone',
    header: 'Telefon',
    cell: ({ row }) => {
      return (
        <div className="text-sm font-mono">{row.original.userPhone || '-'}</div>
      );
    },
  },
  {
    accessorKey: 'latestUserText',
    header: 'Letzter Nutzer',
    cell: ({ row }) => {
      return (
        <div className="max-w-xs truncate text-sm" title={row.original.latestUserText || undefined}>
          {truncateText(row.original.latestUserText, 50)}
        </div>
      );
    },
  },
  {
    accessorKey: 'latestAssistantText',
    header: 'Letzter Assistant',
    cell: ({ row }) => {
      return (
        <div className="max-w-xs truncate text-sm" title={row.original.latestAssistantText || undefined}>
          {truncateText(row.original.latestAssistantText, 50)}
        </div>
      );
    },
  },
  {
    accessorKey: 'transcriptAvailable',
    header: 'Transcript',
    cell: ({ row }) => {
      return row.original.transcriptAvailable ? (
        <Badge variant="outline" className="text-muted-foreground px-1.5">
          <IconFileText className="mr-1 size-3" />
          Verfügbar
        </Badge>
      ) : (
        <span className="text-muted-foreground text-sm">-</span>
      );
    },
  },
  {
    id: 'actions',
    cell: ({ row }) => {
      const conversation = row.original;
      return (
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button
              variant="ghost"
              className="data-[state=open]:bg-muted text-muted-foreground flex size-8"
              size="icon"
            >
              <IconDotsVertical />
              <span className="sr-only">Menü öffnen</span>
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end" className="w-48">
            {conversation.transcriptAvailable && (
              <>
                <DropdownMenuItem
                  onClick={() => {
                    const url = buildConversationDownloadUrl(conversation.id, 'json');
                    window.open(url, '_blank');
                  }}
                >
                  <IconFileCode className="mr-2 size-4" />
                  JSON herunterladen
                </DropdownMenuItem>
                <DropdownMenuItem
                  onClick={() => {
                    const url = buildConversationDownloadUrl(conversation.id, 'txt');
                    window.open(url, '_blank');
                  }}
                >
                  <IconFileText className="mr-2 size-4" />
                  TXT herunterladen
                </DropdownMenuItem>
                <DropdownMenuSeparator />
              </>
            )}
            <DropdownMenuItem
              onClick={() => {
                toast.info(`Detailansicht für Gespräch ${conversation.id} wird später implementiert`);
              }}
            >
              Details anzeigen
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      );
    },
  },
];

interface ConversationsTableProps {
  initial: ConversationsListView;
  page: number;
  limit: number;
}

export function ConversationsTable({ initial, page, limit }: ConversationsTableProps) {
  const router = useRouter();
  const [data] = React.useState(() => initial.items);
  const [rowSelection, setRowSelection] = React.useState({});
  const [columnVisibility, setColumnVisibility] = React.useState<VisibilityState>({});
  const [columnFilters, setColumnFilters] = React.useState<ColumnFiltersState>([]);
  const [sorting, setSorting] = React.useState<SortingState>([]);
  const [globalFilter, setGlobalFilter] = React.useState('');

  const totalPages = Math.max(1, Math.ceil(initial.total / limit));

  const table = useReactTable({
    data,
    columns,
    state: {
      sorting,
      columnVisibility,
      rowSelection,
      columnFilters,
      globalFilter,
    },
    getRowId: (row) => row.id.toString(),
    enableRowSelection: true,
    onRowSelectionChange: setRowSelection,
    onSortingChange: setSorting,
    onColumnFiltersChange: setColumnFilters,
    onColumnVisibilityChange: setColumnVisibility,
    onGlobalFilterChange: setGlobalFilter,
    getCoreRowModel: getCoreRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getFacetedRowModel: getFacetedRowModel(),
    getFacetedUniqueValues: getFacetedUniqueValues(),
    manualPagination: true,
    pageCount: totalPages,
  });

  const handlePageChange = (newPage: number) => {
    router.push(`/conversations?page=${newPage}&limit=${limit}`);
  };

  const handleLimitChange = (newLimit: string) => {
    router.push(`/conversations?page=1&limit=${newLimit}`);
  };

  return (
    <div className="flex w-full flex-col justify-start gap-6">
      <div className="flex items-center justify-between px-4 lg:px-6">
        <div className="flex flex-1 items-center gap-2">
          <Input
            placeholder="Gespräche durchsuchen..."
            value={globalFilter ?? ''}
            onChange={(event) => setGlobalFilter(String(event.target.value))}
            className="max-w-sm"
          />
        </div>
        <div className="flex items-center gap-2">
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="outline" size="sm">
                <IconLayoutColumns />
                <span className="hidden lg:inline">Spalten anpassen</span>
                <span className="lg:hidden">Spalten</span>
                <IconChevronDown />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-56">
              {table
                .getAllColumns()
                .filter(
                  (column) =>
                    typeof column.accessorFn !== 'undefined' && column.getCanHide()
                )
                .map((column) => {
                  return (
                    <DropdownMenuCheckboxItem
                      key={column.id}
                      className="capitalize"
                      checked={column.getIsVisible()}
                      onCheckedChange={(value) => column.toggleVisibility(!!value)}
                    >
                      {column.id}
                    </DropdownMenuCheckboxItem>
                  );
                })}
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </div>
      <div className="relative flex flex-col gap-4 overflow-auto px-4 lg:px-6">
        <div className="overflow-hidden rounded-lg border">
          <Table>
            <TableHeader className="bg-muted sticky top-0 z-10">
              {table.getHeaderGroups().map((headerGroup) => (
                <TableRow key={headerGroup.id}>
                  {headerGroup.headers.map((header) => {
                    return (
                      <TableHead key={header.id} colSpan={header.colSpan}>
                        {header.isPlaceholder
                          ? null
                          : flexRender(header.column.columnDef.header, header.getContext())}
                      </TableHead>
                    );
                  })}
                </TableRow>
              ))}
            </TableHeader>
            <TableBody>
              {table.getRowModel().rows?.length ? (
                table.getRowModel().rows.map((row) => (
                  <TableRow
                    key={row.id}
                    data-state={row.getIsSelected() && 'selected'}
                  >
                    {row.getVisibleCells().map((cell) => (
                      <TableCell key={cell.id}>
                        {flexRender(cell.column.columnDef.cell, cell.getContext())}
                      </TableCell>
                    ))}
                  </TableRow>
                ))
              ) : (
                <TableRow>
                  <TableCell colSpan={columns.length} className="h-24 text-center">
                    Keine Ergebnisse.
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </div>
        <div className="flex items-center justify-between px-4">
          <div className="text-muted-foreground hidden flex-1 text-sm lg:flex">
            {table.getFilteredSelectedRowModel().rows.length} von{' '}
            {table.getFilteredRowModel().rows.length} Zeile(n) ausgewählt.
          </div>
          <div className="flex w-full items-center gap-8 lg:w-fit">
            <div className="hidden items-center gap-2 lg:flex">
              <Label htmlFor="rows-per-page" className="text-sm font-medium">
                Zeilen pro Seite
              </Label>
              <Select value={`${limit}`} onValueChange={handleLimitChange}>
                <SelectTrigger size="sm" className="w-20" id="rows-per-page">
                  <SelectValue placeholder={limit} />
                </SelectTrigger>
                <SelectContent side="top">
                  {[10, 20, 30, 40, 50].map((pageSize) => (
                    <SelectItem key={pageSize} value={`${pageSize}`}>
                      {pageSize}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="flex w-fit items-center justify-center text-sm font-medium">
              Seite {page} von {totalPages}
            </div>
            <div className="ml-auto flex items-center gap-2 lg:ml-0">
              <Button
                variant="outline"
                className="hidden h-8 w-8 p-0 lg:flex"
                onClick={() => handlePageChange(1)}
                disabled={page <= 1}
              >
                <span className="sr-only">Zur ersten Seite</span>
                <IconChevronsLeft />
              </Button>
              <Button
                variant="outline"
                className="size-8"
                size="icon"
                onClick={() => handlePageChange(page - 1)}
                disabled={page <= 1}
              >
                <span className="sr-only">Zur vorherigen Seite</span>
                <IconChevronLeft />
              </Button>
              <Button
                variant="outline"
                className="size-8"
                size="icon"
                onClick={() => handlePageChange(page + 1)}
                disabled={page >= totalPages}
              >
                <span className="sr-only">Zur nächsten Seite</span>
                <IconChevronRight />
              </Button>
              <Button
                variant="outline"
                className="hidden size-8 lg:flex"
                size="icon"
                onClick={() => handlePageChange(totalPages)}
                disabled={page >= totalPages}
              >
                <span className="sr-only">Zur letzten Seite</span>
                <IconChevronsRight />
              </Button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

