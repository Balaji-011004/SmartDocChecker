import React from 'react';
import ContradictionItem from './ContradictionItem';

/**
 * AnalysisResults – displays the summary statistics and the list of contradictions.
 *
 * Props:
 *   results       – { totalContradictions, averageConfidence, analysisTime, contradictions,
 *                     isMultiDoc?, documents?, totalClauses? }
 *   onNewAnalysis – callback to reset and start over
 *   onDownload    – callback to download the PDF report
 */
export default function AnalysisResults({ results, onNewAnalysis, onDownload }) {
    return (
        <div className="analysis-results">
            {/* Header */}
            <div className="results-header">
                <h2>{results.isMultiDoc ? 'Comparison Complete' : 'Analysis Complete'}</h2>
                <div className="results-actions">
                    <button className="action-btn secondary" onClick={onNewAnalysis}>
                        <i className="fas fa-plus"></i>
                        New Analysis
                    </button>
                    <button className="action-btn primary" onClick={onDownload}>
                        <i className="fas fa-download"></i>
                        Download Report
                    </button>
                </div>
            </div>

            {/* Compared documents (multi-doc only) */}
            {results.isMultiDoc && results.documents && results.documents.length > 0 && (
                <div className="compared-documents">
                    <h3><i className="fas fa-exchange-alt"></i> Compared Documents</h3>
                    <div className="doc-chips">
                        {results.documents.map((doc, idx) => (
                            <span key={doc.id || idx} className="doc-chip">
                                <i className="fas fa-file-alt"></i> {doc.name}
                            </span>
                        ))}
                    </div>
                </div>
            )}

            {/* Summary stats */}
            <div className="results-summary">
                <div className="summary-card">
                    <div className="summary-stat">
                        <h3>{results.totalContradictions}</h3>
                        <p>{results.isMultiDoc ? 'Cross-Doc Contradictions' : 'Contradictions Found'}</p>
                    </div>
                    {results.totalClauses > 0 && (
                        <div className="summary-stat">
                            <h3>{results.totalClauses}</h3>
                            <p>Clauses Analyzed</p>
                        </div>
                    )}
                    <div className="summary-stat">
                        <h3>{results.averageConfidence}%</h3>
                        <p>Avg Confidence</p>
                    </div>
                    <div className="summary-stat">
                        <h3>{results.analysisTime}</h3>
                        <p>Analysis Time</p>
                    </div>
                </div>
            </div>

            {/* Contradictions list */}
            <div className="contradictions-list">
                {(!results.contradictions || (Array.isArray(results.contradictions) && results.contradictions.length === 0) || (typeof results.contradictions === 'object' && !Array.isArray(results.contradictions) && Object.values(results.contradictions).every(arr => Array.isArray(arr) && arr.length === 0))) ? (
                    <div className="no-contradictions">
                        <i className="fas fa-check-circle"></i>
                        <h3>No contradictions found!</h3>
                        <p>
                            {results.isMultiDoc
                                ? 'The compared documents appear to be consistent with each other.'
                                : 'This document appears to be consistent and free of contradictions.'}
                        </p>
                    </div>
                ) : Array.isArray(results.contradictions) ? (
                    results.contradictions.map((item, idx) => (
                        <ContradictionItem key={idx} contradiction={item} isMultiDoc={results.isMultiDoc} />
                    ))
                ) : (
                    Object.entries(results.contradictions).map(([severity, items]) => (
                        items && items.length > 0 && (
                            <div key={severity} className={`severity-group severity-${severity}`}>
                                <h3 className="severity-title">
                                    {(String(severity)).charAt(0).toUpperCase() + (String(severity)).slice(1)} Severity
                                </h3>
                                {items.map((item) => (
                                    <ContradictionItem key={item.id} contradiction={item} isMultiDoc={results.isMultiDoc} />
                                ))}
                            </div>
                        )
                    ))
                )}
            </div>
        </div>
    );
}
