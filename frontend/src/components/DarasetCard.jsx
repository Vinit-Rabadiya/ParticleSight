function DatasetCard({ dataset, onAnalyze }) {
    return (
        <div className="dataset-card">
            <h2>Dataset: {dataset.name}</h2>
            <p>Description: {dataset.description}</p>
            <p>Dataset ID: {dataset.id}</p>
            <p>Year: {dataset.year}</p>
            <p>Experiment: {dataset.experiment}</p>
            <p>DOI URL: <a href={dataset.doi_url} target="_blank" rel="noopener noreferrer">{dataset.doi_url}</a>View on CERN</p>
            <button onClick={onAnalyze}>Analyze</button>
        </div>
    );
}