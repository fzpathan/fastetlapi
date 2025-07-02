

<details>
<summary>📄 Click to expand full README.md content</summary># 📊 Dynamic AG Grid Component (React + TypeScript + Tailwind)

A powerful, reusable, and fully dynamic data grid component built using [AG Grid](https://www.ag-grid.com/), [React](https://reactjs.org/), [TypeScript](https://www.typescriptlang.org/), and [TailwindCSS](https://tailwindcss.com/).

Supports dynamic datasets, smart auto-height, tooltips, CSV export, column layout persistence, and responsive styling.

---

## 🚀 Features

- ✅ Dynamic column detection (based on dataset keys)
- ✅ Auto height and text wrapping for long content
- ✅ Tooltips on hover using a custom tooltip component
- ✅ Sorting, filtering, column visibility toggling
- ✅ Column pinning and layout persistence via `localStorage`
- ✅ CSV export
- ✅ TailwindCSS-based layout and styling
- ✅ Layout reset button
- ✅ Plug-and-play for any JSON data source

---

## 📦 Installation

```bash
npm install ag-grid-community ag-grid-react
npm install tailwindcss postcss autoprefixer

Ensure Tailwind is configured in your project. If not, run:

npx tailwindcss init -p

Then add Tailwind to your CSS:

/* ./src/index.css */
@tailwind base;
@tailwind components;
@tailwind utilities;


---

## 🧱 Usage

1. Import the component

import DynamicAgGrid from './components/DynamicAgGrid';

2. Use with any JSON dataset

const data = [
  { name: 'Apple', category: 'Fruit', description: 'A juicy red fruit', price: 1.2 },
  { name: 'Banana', category: 'Fruit', description: 'Long yellow fruit', price: 0.5 },
  {
    name: 'Watermelon',
    category: 'Fruit',
    description: 'Very large green fruit '.repeat(30),
    price: 3.5,
  },
];

<DynamicAgGrid data={data} storageKey="fruit-grid-layout" />;

> ℹ️ storageKey is optional — it's used to persist column layout (visibility, order, pinning, etc.)




---

## 🧪 Component Props

Prop	Type	Required	Description

data	Record<string, any>[]	✅	The dataset to display
storageKey	string	❌	Key used for saving layout state



---

🖼️ Preview




---

## 📤 Features in Action

Long text fields auto-wrap:

description: 'This is a really long description...'.repeat(20)

Layout persistence:

Reorder or hide columns

Hit Save Layout

Refresh page — changes remain!

Use Reset Layout to restore default


CSV Export:

Click Export CSV

Downloads visible data as .csv file




---

## 🧰 Developer Notes

Built with:

React 18+

TypeScript 5+

AG Grid Community

TailwindCSS


Component file: DynamicAgGrid.tsx



---

## 📁 Project Structure

src/
├── components/
│   └── DynamicAgGrid.tsx
├── App.tsx
├── index.tsx
└── tailwind.config.js


---

## 📜 License

MIT — Feel free to use and customize!


---

## 🤝 Contributions

If you find a bug or have a feature request, feel free to open an issue or submit a PR.


---

## ✨ Author

You — powered by AG Grid + React + ChatGPT 😄

</details>

3. Save it as `README.md` in your project root.

---

Let me know if you'd like:
- A PDF version of this README
- Deployment steps (e.g. for GitHub Pages, Vercel, etc.)
- To auto-generate this from a CLI script

