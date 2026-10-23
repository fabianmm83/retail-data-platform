import { Route, Routes } from 'react-router-dom';

import Layout from './components/Layout';
import Overview from './pages/Overview';
import Sales from './pages/Sales';
import Products from './pages/Products';
import States from './pages/States';
import Channels from './pages/Channels';

function App() {
  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        <Route index element={<Overview />} />
        <Route path="sales" element={<Sales />} />
        <Route path="products" element={<Products />} />
        <Route path="states" element={<States />} />
        <Route path="channels" element={<Channels />} />
      </Route>
    </Routes>
  );
}

export default App;