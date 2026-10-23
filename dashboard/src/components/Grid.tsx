interface GridProps {
  children: React.ReactNode;
  cols?: 1 | 2 | 3 | 4;
  gap?: 4 | 6 | 8;
}

const COLS_CLASSES = {
  1: 'grid-cols-1',
  2: 'grid-cols-1 sm:grid-cols-2',
  3: 'grid-cols-1 sm:grid-cols-2 lg:grid-cols-3',
  4: 'grid-cols-1 sm:grid-cols-2 lg:grid-cols-4',
};

const GAP_CLASSES = {
  4: 'gap-4',
  6: 'gap-6',
  8: 'gap-8',
};

export default function Grid({ children, cols = 4, gap = 4 }: GridProps) {
  return (
    <div className={`grid ${COLS_CLASSES[cols]} ${GAP_CLASSES[gap]}`}>
      {children}
    </div>
  );
}