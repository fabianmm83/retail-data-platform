interface ErrorStateProps {
  message?: string;
}

export default function ErrorState({ message }: ErrorStateProps) {
  return (
    <div className="card bg-red-50 border-red-200">
      <p className="text-sm font-medium text-red-800">Error cargando datos</p>
      <p className="text-xs text-red-600 mt-1">
        {message || 'Verifica que la API esté corriendo en el puerto 8001.'}
      </p>
    </div>
  );
}