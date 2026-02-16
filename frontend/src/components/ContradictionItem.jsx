import React from 'react';

/**
 * ContradictionItem – a single contradiction card with type/severity badges,
 * confidence bar, document snippets, and an explanation.
 *
 * Props:
 *   contradiction – {
 *     type, severity, confidence, description,
 *     // Single-doc format:
 *     clause_a: { id, text }, clause_b: { id, text },
 *     // Multi-doc format:
 *     document_a: { id, name }, document_b: { id, name },
 *     // Legacy format:
 *     document1: { name, text }, document2: { name, text },
 *   }
 *   isMultiDoc – whether this is a cross-document contradiction
 */
export default function ContradictionItem({ contradiction, isMultiDoc }) {
    // Determine source labels
    const labelA = isMultiDoc && contradiction.document_a
        ? contradiction.document_a.name
        : (contradiction.document1 && contradiction.document1.name) || 'Source A';

    const labelB = isMultiDoc && contradiction.document_b
        ? contradiction.document_b.name
        : (contradiction.document2 && contradiction.document2.name) || 'Source B';

    const textA = contradiction.clause_a
        ? contradiction.clause_a.text
        : (contradiction.document1 ? contradiction.document1.text : '');

    const textB = contradiction.clause_b
        ? contradiction.clause_b.text
        : (contradiction.document2 ? contradiction.document2.text : '');

    // Confidence is stored as 0-100 from backend
    const confidencePct = Math.round(contradiction.confidence || 0);

    const typeLabels = {
        semantic: 'Semantic',
        numeric: 'Numeric',
        modal: 'Modal',
        authority: 'Authority',
        date: 'Date / Time',
        financial: 'Financial',
        entity: 'Entity',
        location: 'Location',
        quantity: 'Quantity',
    };
    const typeLabel = typeLabels[contradiction.type] || contradiction.type || 'Unknown';

    return (
        <div className="contradiction-item">
            <div className="contradiction-header">
                <div className="contradiction-type">
                    <span className={`type-badge ${contradiction.type || 'unknown'}`}>
                        {typeLabel}
                    </span>
                    <span className={`severity-badge ${contradiction.severity || 'medium'}`}>
                        {contradiction.severity || 'Medium'}
                    </span>
                    {isMultiDoc && (
                        <span className="type-badge cross-doc">Cross-Doc</span>
                    )}
                </div>
                <div className="confidence-score">
                    <span>Confidence:</span>
                    <div className="confidence-bar">
                        <div
                            className="confidence-fill"
                            style={{ width: `${confidencePct}%` }}
                        ></div>
                    </div>
                    <span>{confidencePct}%</span>
                </div>
            </div>

            <div className="contradiction-content">
                {textA && (
                    <div className="document-snippet">
                        <h4><i className="fas fa-file-alt"></i> {labelA}</h4>
                        <p>"{textA}"</p>
                    </div>
                )}
                {textB && (
                    <div className="document-snippet">
                        <h4><i className="fas fa-file-alt"></i> {labelB}</h4>
                        <p>"{textB}"</p>
                    </div>
                )}
            </div>

            <div className="contradiction-explanation">
                <p>{contradiction.explanation || contradiction.description || 'No explanation provided.'}</p>
            </div>
        </div>
    );
}
