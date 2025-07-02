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

// ✅ Tooltip
const CustomTooltip: React.FC<ITooltipParams> = ({ value }) => {
  const text = String(value || '');
  const maxLength = 200;
  return (
    <div className="whitespace-normal max-w-[400px] p-2 text-sm">
      {text.length > maxLength ? text.substring(0, maxLength) + '...' : text}
    </div>
  );
};

// ✅ Row data type
interface RowDataType {
  id: number;
  name: string;
  description: string;
  shortNote: string;
  comments: string;
}

type ViewType = 'full' | 'commentsOnly' | 'summary';

const MultiGridComponent: React.FC = () => {
  const gridRef = useRef<AgGridReact<RowDataType>>(null);
  const [rowData, setRowData] = useState<RowDataType[]>([]);
  const [columnDefs, setColumnDefs] = useState<ColDef[]>([]);
  const [selectedView, setSelectedView] = useState<ViewType>('full');

  useEffect(() => {
    const data: RowDataType[] = Array.from({ length: 1000 }).map((_, i) => ({
      id: i + 1,
      name: `Item ${i + 1}`,
      description: `This is a long description for row ${i + 1}. `.repeat(10),
      shortNote: `Note ${i + 1}`,
      comments: i % 10 === 0 ? `Long comment: `.repeat(30) : `Short comment`,
    }));
    setRowData(data);
  }, []);

  useEffect(() => {
    if (rowData.length === 0) return;

    const longTextCols = new Set<string>();
    for (const row of rowData) {
      for (const [key, value] of Object.entries(row)) {
        if (String(value).length > 300) {
          longTextCols.add(key);
        }
      }
    }

    let fields: (keyof RowDataType)[];
    switch (selectedView) {
      case 'commentsOnly':
        fields = ['id', 'comments'];
        break;
      case 'summary':
        fields = ['id', 'name', 'shortNote'];
        break;
      default:
        fields = ['id', 'name', 'description', 'shortNote', 'comments'];
    }

    const generatedCols: ColDef[] = fields.map((key) => {
      const isLong = longTextCols.has(key);
      return {
        field: key,
        headerName: key.charAt(0).toUpperCase() + key.slice(1),
        width: 200,
        wrapText: isLong,
        autoHeight: isLong,
        tooltipField: key,
        tooltipComponent: 'customTooltip',
        pinned: key === 'id' ? 'left' : undefined,
        cellStyle: isLong ? { whiteSpace: 'normal' } : undefined,
        sortable: true,
        filter: true,
        resizable: true,
      };
    });

    setColumnDefs(generatedCols);
  }, [selectedView, rowData]);

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
      localStorage.setItem(`layout-${selectedView}`, JSON.stringify(state));
      console.log(`✅ Layout saved for "${selectedView}"`);
    }
  };

  const resetLayout = () => {
    localStorage.removeItem(`layout-${selectedView}`);
    setSelectedView((prev) => prev); // force re-render
    console.log(`🧹 Layout reset for "${selectedView}"`);
  };

  const onGridReady = (params: GridReadyEvent) => {
    const saved = localStorage.getItem(`layout-${selectedView}`);
    if (saved) {
      const parsed = JSON.parse(saved) as ColumnState[];
      params.columnApi.applyColumnState({
        state: parsed,
        applyOrder: true,
      });
    }
  };

  return (
    <div className="w-full overflow-x-auto p-4">
      {/* ✅ Tabs */}
      <div className="flex justify-between items-center mb-4">
        <div className="flex space-x-3">
          {(['full', 'commentsOnly', 'summary'] as ViewType[]).map((view) => (
            <button
              key={view}
              className={`px-4 py-2 rounded-md text-sm font-medium transition
                ${selectedView === view
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-200 text-gray-800 hover:bg-gray-300'}`}
              onClick={() => setSelectedView(view)}
            >
              {view === 'full' && 'Full View'}
              {view === 'commentsOnly' && 'Comments Only'}
              {view === 'summary' && 'Summary'}
            </button>
          ))}
        </div>

        {/* ✅ Action Buttons */}
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

      {/* ✅ AG Grid */}
      <div className="ag-theme-alpine w-full" style={{ height: '600px' }}>
        <AgGridReact<RowDataType>
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
          key={selectedView}
        />
      </div>
    </div>
  );
};

export default MultiGridComponent;
