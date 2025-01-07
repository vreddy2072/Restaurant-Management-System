import React from 'react';
import {
  Table as MUITable,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  IconButton,
} from '@mui/material';
import {
  KeyboardArrowUp,
  KeyboardArrowDown,
  Edit,
  Delete,
} from '@mui/icons-material';

interface Column {
  id: string;
  label: string;
  sortable?: boolean;
}

interface TableProps {
  columns: Column[];
  data: any[];
  onSort?: (column: string) => void;
  sortColumn?: string;
  sortDirection?: 'asc' | 'desc';
  onEdit?: (row: any) => void;
  onDelete?: (row: any) => void;
}

const Table: React.FC<TableProps> = ({
  columns,
  data,
  onSort,
  sortColumn,
  sortDirection,
  onEdit,
  onDelete,
}) => {
  return (
    <TableContainer component={Paper}>
      <MUITable>
        <TableHead>
          <TableRow>
            {columns.map((column) => (
              <TableCell
                key={column.id}
                onClick={() => column.sortable && onSort?.(column.id)}
                style={{ cursor: column.sortable ? 'pointer' : 'default' }}
              >
                {column.label}
                {column.sortable && sortColumn === column.id && (
                  <IconButton size="small">
                    {sortDirection === 'asc' ? (
                      <KeyboardArrowUp />
                    ) : (
                      <KeyboardArrowDown />
                    )}
                  </IconButton>
                )}
              </TableCell>
            ))}
            {(onEdit || onDelete) && <TableCell>Actions</TableCell>}
          </TableRow>
        </TableHead>
        <TableBody>
          {data.map((row, index) => (
            <TableRow key={index}>
              {columns.map((column) => (
                <TableCell key={column.id}>{row[column.id]}</TableCell>
              ))}
              {(onEdit || onDelete) && (
                <TableCell>
                  {onEdit && (
                    <IconButton onClick={() => onEdit(row)}>
                      <Edit />
                    </IconButton>
                  )}
                  {onDelete && (
                    <IconButton onClick={() => onDelete(row)}>
                      <Delete />
                    </IconButton>
                  )}
                </TableCell>
              )}
            </TableRow>
          ))}
        </TableBody>
      </MUITable>
    </TableContainer>
  );
};

export default Table; 