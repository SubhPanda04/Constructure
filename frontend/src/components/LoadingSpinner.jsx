const LoadingSpinner = ({ message = 'Loading...' }) => {
    return (
        <div className="flex items-center justify-center space-x-2 py-4">
            <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-primary-600"></div>
            <span className="text-sm text-gray-600">{message}</span>
        </div>
    );
};

export default LoadingSpinner;
