interface PageHeaderProps {
  title: string;
  subtitle?: string;
}

export default function PageHeader({ title, subtitle }: PageHeaderProps) {
  return (
    <header className="mb-8">
      <h2 className="text-2xl font-bold text-gray-900">{title}</h2>
      {subtitle && <p className="text-sm text-gray-500 mt-1">{subtitle}</p>}
    </header>
  );
}