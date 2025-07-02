import React, { useEffect, useState, useRef, useMemo } from 'react';
import { AgGridReact } from 'ag-grid-react';
import {
  ColDef,
  ColumnState,
  GridReadyEvent,
  ITooltipParams,
} from 'ag-grid-community';
import 'ag-grid-community/styles/ag-grid.css';
import 'ag-grid-community/styles/ag-theme-alpine.css';

// ✅ Tooltip component
const CustomTooltip: React.FC<ITooltipParams> = ({ value }) => {
  const text = String(value || '');
  const maxLength = 200;
  return (
    <div className="whitespace-normal max-w-[400px] p-2 text-sm">
      {text.length > maxLength ? text.substring(0, maxLength) + '...' : text}
    </div>
  );
};

const MultiGridComponent: React.FC = () => {
  const gridRef = useRef<AgGridReact>(null);
  const [rowData, setRowData] = useState<any[]>([]);
  const [columnDefs, setColumnDefs] = useState<ColDef[]>([]);
  const [layoutKey, setLayoutKey] = useState('default');

  // ✅ Simulated dynamic dataset
  useEffect(() => {
    const generateData = () => {
      const rows = [];
      for (let i = 0; i < 1000; i++) {
        rows.push({
          [`col_${i % 10}`]: `Short ${i}`,
          [`text_block_${i % 3}`]: i % 5 === 0 ? 'This is a very long cell text '.repeat(20) : `Text ${i}`,
        });
      }
      return rows;
    };

    const data = generateData();
    setRowData(data);

    if (data.length > 0) {
      const longColumns = new Set<string>();

      for (const row of data) {
        for (const [key, value] of Object.entries(row)) {
          if (String(value).length > 300) {
            longColumns.add(key);
          }
        }
      }

      const dynamicCols: ColDef[] = Object.keys(data[0]).map((key) => {
        const isLong = longColumns.has(key);
        return {
          field: key,
          headerName: key,
          width: 200,
          wrapText: isLong,
          autoHeight: isLong,
          tooltipField: key,
          tooltipComponent: 'customTooltip',
          pinned: undefined, // No default pin
          cellStyle: isLong ? { whiteSpace: 'normal' } : undefined,
          sortable: true,
          filter: true,
          resizable: true,
        };
      });

      setColumnDefs(dynamicCols);
    }
  }, []);

  // ✅ Default column settings
  const defaultColDef: ColDef = useMemo(() => ({
    resizable: true,
    sortable: true,
    filter: true,
    tooltipComponent: 'customTooltip',
  }), []);

  const handleExport = () => {
    gridRef.current?.api.exportDataAsCsv();
  };

  const saveLayout = () => {
    const state = gridRef.current?.columnApi.getColumnState();
    if (state) {
      localStorage.setItem(`layout-${layoutKey}`, JSON.stringify(state));
      console.log('✅ Layout saved');
    }
  };

  const resetLayout = () => {
    localStorage.removeItem(`layout-${layoutKey}`);
    setLayoutKey(prev => prev + '_reset'); // trigger remount
    console.log('🧹 Layout reset');
  };

  const onGridReady = (params: GridReadyEvent) => {
    const saved = localStorage.getItem(`layout-${layoutKey}`);
    if (saved) {
      const parsed = JSON.parse(saved) as ColumnState[];
      params.columnApi.applyColumnState({
        state: parsed,
        applyOrder: true,
      });
      console.log('🔁 Layout restored');
    }
  };

  return (
    <div className="w-full overflow-x-auto p-4">
      {/* Header Controls */}
      <div className="flex justify-between items-center mb-4">
        <div className="text-lg font-semibold">📊 Dynamic Grid</div>
        <div className="flex space-x-2">
          <button
            onClick={handleExport}
            className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700 text-sm"
          >
            Export CSV
          </button>
          <button
            onClick={saveLayout}
            className="bg-yellow-500 text-white px-4 py-2 rounded hover:bg-yellow-600 text-sm"
          >
            Save Layout
          </button>
          <button
            onClick={resetLayout}
            className="bg-red-500 text-white px-4 py-2 rounded hover:bg-red-600 text-sm"
          >
            Reset Layout
          </button>
        </div>
      </div>

      {/* AG Grid */}
      <div className="ag-theme-alpine w-full" style={{ height: '600px' }}>
        <AgGridReact
          ref={gridRef}
          rowData={rowData}
          columnDefs={columnDefs}
          defaultColDef={defaultColDef}
          frameworkComponents={{ customTooltip: CustomTooltip }}
          suppressHorizontalScroll={false}
          domLayout="normal"
          rowBuffer={10}
          animateRows={true}
          onGridReady={onGridReady}
          enableBrowserTooltips={false}
          key={layoutKey} // Force re-mount when layout is reset
        />
      </div>
    </div>
  );
};

export default MultiGridComponent;
