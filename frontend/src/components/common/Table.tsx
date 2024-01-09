import React from 'react';
import {
  ChevronUpDownIcon,
  ChevronUpIcon,
  ChevronDownIcon,
} from '@heroicons/react/24/outline';

export interface Column<T> {
  key: keyof T | string;
  title: string;
  render?: (item: T) => React.ReactNode;
  sortable?: boolean;
  width?: string;
}

interface TableProps<T> {
  columns: Column<T>[];
  data: T[];
  onSort?: (key: keyof T | string, direction: 'asc' | 'desc') => void;
  sortColumn?: string;
  sortDirection?: 'asc' | 'desc';
  isLoading?: boolean;
  emptyMessage?: string;
  rowClassName?: string | ((item: T) => string);
  onRowClick?: (item: T) => void;
}

const Table = <T extends Record<string, any>>({
  columns,
  data,
  onSort,
  sortColumn,
  sortDirection,
  isLoading = false,
  emptyMessage = 'No data available',
  rowClassName,
  onRowClick,
}: TableProps<T>) => {
  const handleSort = (column: Column<T>) => {
    if (!column.sortable || !onSort) return;

    const key = column.key;
    const newDirection =
      sortColumn === key && sortDirection === 'asc' ? 'desc' : 'asc';
    onSort(key, newDirection);
  };

  const getSortIcon = (column: Column<T>) => {
    if (!column.sortable) return null;

    if (sortColumn === column.key) {
      return sortDirection === 'asc' ? (
        <ChevronUpIcon className="h-4 w-4" />
      ) : (
        <ChevronDownIcon className="h-4 w-4" />
      );
    }
    return <ChevronUpDownIcon className="h-4 w-4" />;
  };

  const getRowClassName = (item: T) => {
    if (typeof rowClassName === 'function') {
      return rowClassName(item);
    }
    return rowClassName || '';
  };

  if (isLoading) {
    return (
      <div className="min-h-[200px] flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    );
  }

  if (!data.length) {
    return (
      <div className="min-h-[200px] flex items-center justify-center text-text-light">
        {emptyMessage}
      </div>
    );
  }

  return (
    <div className="overflow-x-auto">
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-surface">
          <tr>
            {columns.map((column) => (
              <th
                key={column.key.toString()}
                scope="col"
                className={`px-6 py-3 text-left text-xs font-medium text-text-light uppercase tracking-wider ${
                  column.sortable ? 'cursor-pointer select-none' : ''
                }`}
                style={{ width: column.width }}
                onClick={() => handleSort(column)}
              >
                <div className="flex items-center space-x-1">
                  <span>{column.title}</span>
                  {getSortIcon(column)}
                </div>
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="bg-surface divide-y divide-gray-200">
          {data.map((item, index) => (
            <tr
              key={index}
              className={`${
                onRowClick ? 'cursor-pointer hover:bg-gray-50' : ''
              } ${getRowClassName(item)}`}
              onClick={() => onRowClick?.(item)}
            >
              {columns.map((column) => (
                <td
                  key={`${index}-${column.key.toString()}`}
                  className="px-6 py-4 whitespace-nowrap text-sm text-text"
                >
                  {column.render
                    ? column.render(item)
                    : item[column.key as keyof T]}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default Table; 