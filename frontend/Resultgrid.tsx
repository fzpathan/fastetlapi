// src/components/ResultGrid.tsx

import React from 'react';
import { AgGridReact } from 'ag-grid-react';
import 'ag-grid-community/styles/ag-grid.css';
import 'ag-grid-community/styles/ag-theme-alpine.css';

export interface ResultGridProps {
  result: Record<string, any>[];  // Accepts a list of dictionaries
}

const ResultGrid: React.FC<ResultGridProps> = ({ result }) => {
  if (!Array.isArray(result) || result.length === 0) {
    return <div className="text-slate-400">No results to display</div>;
  }

  const columnDefs = Object.keys(result[0]).map((key) => ({
    headerName: key.charAt(0).toUpperCase() + key.slice(1),
    field: key,
  }));

  return (
    <div>
      <h3 className="text-emerald-400 font-medium mb-2">Calculation Results:</h3>
      <div className="ag-theme-alpine" style={{ height: 400, width: '100%' }}>
        <AgGridReact
          rowData={result}
          columnDefs={columnDefs}
          defaultColDef={{
            flex: 1,
            sortable: true,
            filter: true,
            resizable: true,
          }}
        />
      </div>
    </div>
  );
};

export default ResultGrid;

import React from 'react';
import ResultGrid from './components/ResultGrid'; // Adjust path as needed

interface NodeData {
  output?: {
    result?: Record<string, any>[];
  };
}

interface NodeOutputViewerProps {
  selectedNode: {
    data: NodeData;
  };
}

const NodeOutputViewer: React.FC<NodeOutputViewerProps> = ({ selectedNode }) => {
  const result = selectedNode.data.output?.result;

  return result ? (
    <ResultGrid result={result} />
  ) : (
    <div className="flex items-center justify-center h-full text-slate-400">
      Select a node to view its output
    </div>
  );
};

export default NodeOutputViewer;
