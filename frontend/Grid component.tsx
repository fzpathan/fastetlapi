import React, { useState, useEffect, useRef, useMemo } from 'react';
import { AgGridReact } from 'ag-grid-react';
import {
  ColDef,
  ColumnState,
  GridReadyEvent,
  ITooltipParams,
} from 'ag-grid-community';
import 'ag-grid-community/styles/ag-grid.css';
import 'ag-grid-community/styles/ag-theme-alpine.css';

// ✅ Custom Tooltip Component with Props Type
const CustomTooltip: React.FC<ITooltipParams> = ({ value }) => {
  const maxLength = 200;
  const text = value || '';

  return (
    <div style={{ whiteSpace: 'normal', maxWidth: '400px', padding: '5px' }}>
      {String(text).length > maxLength
        ? `${String(text).substring(0, maxLength)}...`
        : String(text)}
    </div>
  );
};

// ✅ Define the row structure (you can extend this)
interface RowDataType {
  id: number;
  name: string;
  description: string;
  shortNote: string;
  comments: string;
}

const GridComponent: React.FC = () => {
  const gridRef = useRef<AgGridReact<RowDataType>>(null);

  const [rowData, setRowData] = useState<RowDataType[]>([]);
  const [columnDefs, setColumnDefs] = useState<ColDef[]>([]);

  // ✅ Load data and dynamically build columns
  useEffect(() => {
    const data: RowDataType[] = Array.from({ length: 1000 }).map((_, i) => ({
      id: i + 1,
      name: `Item ${i + 1}`,
      description: `This is a long description for row ${i + 1}. `.repeat(10),
      shortNote: `Short note ${i + 1}`,
      comments: i % 10 === 0 ? `Long comment: `.repeat(30) : `Short comment`,
    }));

    setRowData(data);

    // 🔍 Detect long text fields (over 300 characters)
    const longTextColumns = new Set<string>();
    for (const row of data) {
      for (const [key, value] of Object.entries(row)) {
        if (String(value).length > 300) {
          longTextColumns.add(key);
        }
      }
    }

    const generatedCols: ColDef[] = Object.keys(data[0]).map((key) => {
      const isLong = longTextColumns.has(key);

      return {
        field: key,
        headerName: key.charAt(0).toUpperCase() + key.slice(1),
        width: 200,
        wrapText: isLong,
        autoHeight: isLong,
        pinned: key === 'id' ? 'left' : undefined,
        tooltipField: key,
        tooltipComponent: 'customTooltip',
        cellStyle: isLong ? { whiteSpace: 'normal' } : undefined,
        sortable: true,
        filter: true,
        resizable: true,
      } as ColDef;
    });

    setColumnDefs(generatedCols);
  }, []);

  // ✅ Default col def with tooltip
  const defaultColDef: ColDef = useMemo(() => ({
    resizable: true,
    sortable: true,
    filter: true,
    tooltipComponent: 'customTooltip',
  }), []);

  // ✅ Export to CSV
  const handleExport = () => {
    gridRef.current?.api.exportDataAsCsv();
  };

  // ✅ Save layout to localStorage
  const saveLayout = () => {
    const colState: ColumnState[] = gridRef.current?.columnApi.getColumnState() || [];
    localStorage.setItem('gridLayout', JSON.stringify(colState));
    console.log('✅ Layout saved');
  };

  // ✅ Restore layout on grid ready
  const onGridReady = (params: GridReadyEvent) => {
    const saved = localStorage.getItem('gridLayout');
    if (saved) {
      const parsedState: ColumnState[] = JSON.parse(saved);
      gridRef.current?.columnApi.applyColumnState({
        state: parsedState,
        applyOrder: true,
      });
      console.log('🔁 Layout restored');
    }
  };

  return (
    <div style={{ width: '100%', overflowX: 'auto' }}>
      <div style={{ marginBottom: 10 }}>
        <button onClick={handleExport}>Export to CSV</button>
        <button onClick={saveLayout} style={{ marginLeft: 10 }}>
          Save Layout
        </button>
        <span style={{ marginLeft: 15, fontSize: '14px' }}>
          <strong>Tip:</strong> Right-click a column header to pin/hide, then "Save Layout"
        </span>
      </div>

      <div className="ag-theme-alpine" style={{ height: '600px', width: '100%' }}>
        <AgGridReact<RowDataType>
          ref={gridRef}
          rowData={rowData}
          columnDefs={columnDefs}
          defaultColDef={defaultColDef}
          suppressHorizontalScroll={false}
          domLayout="normal"
          rowBuffer={10}
          animateRows={true}
          onGridReady={onGridReady}
          frameworkComponents={{ customTooltip: CustomTooltip }}
          enableBrowserTooltips={false}
        />
      </div>
    </div>
  );
};

export default GridComponent;
