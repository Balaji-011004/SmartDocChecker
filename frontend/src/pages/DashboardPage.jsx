import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { fetchDashboardStats } from '../utils/api';

/**
 * DashboardPage – analytics overview with live usage metrics, activity feed,
 * contradiction-type chart, and performance metrics.
 */
export default function DashboardPage() {
    const { token } = useAuth();
    const [stats, setStats] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        let cancelled = false;
        async function load() {
            try {
                setLoading(true);
                const data = await fetchDashboardStats(token);
                if (!cancelled) setStats(data);
            } catch (err) {
                if (!cancelled) setError(err.message);
            } finally {
                if (!cancelled) setLoading(false);
            }
        }
        load();
        return () => { cancelled = true; };
    }, [token]);

    if (loading) {
        return (
            <div id="dashboard-page" className="page active">
                <div className="page-header">
                    <h1>Analytics Dashboard</h1>
                    <p>Loading your analytics...</p>
                </div>
                <div style={{ textAlign: 'center', padding: '3rem' }}>
                    <div className="spinner" />
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div id="dashboard-page" className="page active">
                <div className="page-header">
                    <h1>Analytics Dashboard</h1>
                    <p style={{ color: '#ef4444' }}>Failed to load analytics: {error}</p>
                </div>
            </div>
        );
    }

    const s = stats || {};
    const severityCounts = s.contradictions_by_severity || {};
    const typeCounts = s.contradictions_by_type || {};
    const recentActivity = s.recent_activity || [];

    return (
        <div id="dashboard-page" className="page active">
            <div className="page-header">
                <h1>Analytics Dashboard</h1>
                <p>Monitor your document analysis usage and trends</p>
            </div>

            <div className="dashboard-grid">
                {/* Row 1 – Usage Overview (full width) */}
                <div className="dashboard-card full-row">
                    <div className="card-header">
                        <h3>Usage Overview</h3>
                        <i className="fas fa-chart-bar"></i>
                    </div>
                    <div className="card-content">
                        <div className="metrics-row">
                            <div className="metric">
                                <span className="metric-value">{s.documents_analyzed || 0}</span>
                                <span className="metric-label">Documents Analyzed</span>
                            </div>
                            <div className="metric">
                                <span className="metric-value">{s.total_documents || 0}</span>
                                <span className="metric-label">Total Documents</span>
                            </div>
                            <div className="metric">
                                <span className="metric-value">{s.comparisons_completed || 0}</span>
                                <span className="metric-label">Comparisons Done</span>
                            </div>
                            <div className="metric">
                                <span className="metric-value">{s.total_contradictions || 0}</span>
                                <span className="metric-label">Total Contradictions</span>
                            </div>
                            <div className="metric">
                                <span className="metric-value">{s.single_doc_contradictions || 0}</span>
                                <span className="metric-label">Single-Doc</span>
                            </div>
                            <div className="metric">
                                <span className="metric-value">{s.cross_doc_contradictions || 0}</span>
                                <span className="metric-label">Cross-Doc</span>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Row 2 – Contradiction Types + Performance Metrics */}
                <div className="dashboard-card">
                    <div className="card-header">
                        <h3>Contradiction Types</h3>
                        <i className="fas fa-chart-pie"></i>
                    </div>
                    <div className="card-content">
                        {Object.keys(typeCounts).length === 0 ? (
                            <p style={{ color: '#9ca3af', textAlign: 'center', padding: '1rem' }}>
                                No contradictions detected yet.
                            </p>
                        ) : (
                            <div className="metrics-row">
                                {Object.entries(typeCounts).map(([type, count]) => (
                                    <div key={type} className="metric">
                                        <span className="metric-value">{count}</span>
                                        <span className="metric-label">{type.charAt(0).toUpperCase() + type.slice(1)}</span>
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>
                </div>

                <div className="dashboard-card">
                    <div className="card-header">
                        <h3>Performance Metrics</h3>
                        <i className="fas fa-tachometer-alt"></i>
                    </div>
                    <div className="card-content">
                        <div className="performance-metric">
                            <span className="metric-label">Avg Analysis Time</span>
                            <div className="metric-bar">
                                <div className="metric-fill" style={{ width: `${Math.min((s.avg_analysis_duration || 0) / 60 * 100, 100)}%` }}></div>
                            </div>
                            <span className="metric-value">{s.avg_analysis_duration || 0}s</span>
                        </div>
                        <div className="performance-metric">
                            <span className="metric-label">Total Clauses Processed</span>
                            <div className="metric-bar">
                                <div className="metric-fill success" style={{ width: `${Math.min((s.total_clauses || 0) / 500 * 100, 100)}%` }}></div>
                            </div>
                            <span className="metric-value">{s.total_clauses || 0}</span>
                        </div>
                        <div className="performance-metric">
                            <span className="metric-label">High Severity Issues</span>
                            <div className="metric-bar">
                                <div className="metric-fill" style={{
                                    width: `${s.total_contradictions > 0 ? (severityCounts.high || 0) / s.total_contradictions * 100 : 0}%`,
                                    background: '#ef4444',
                                }}></div>
                            </div>
                            <span className="metric-value">{severityCounts.high || 0}</span>
                        </div>
                    </div>
                </div>

                {/* Row 3 – Recent Activity (full width) */}
                <div className="dashboard-card full-row">
                    <div className="card-header">
                        <h3>Recent Activity</h3>
                        <i className="fas fa-history"></i>
                    </div>
                    <div className="card-content">
                        <div className="activity-list">
                            {recentActivity.length === 0 ? (
                                <p style={{ color: '#9ca3af', textAlign: 'center', padding: '1rem' }}>
                                    No recent activity yet. Analyze a document to get started!
                                </p>
                            ) : (
                                recentActivity.map((item, idx) => (
                                    <div key={idx} className="activity-item">
                                        <div className={`activity-icon ${item.status === 'completed' ? 'success' : 'warning'}`}>
                                            <i className={`fas ${item.status === 'completed'
                                                ? (item.activity_type === 'comparison' ? 'fa-exchange-alt' : 'fa-check')
                                                : 'fa-exclamation'}`}></i>
                                        </div>
                                        <div className="activity-content">
                                            <p>
                                                {item.status === 'completed'
                                                    ? `${item.document_name} — ${item.contradictions_found} contradiction${item.contradictions_found !== 1 ? 's' : ''} found`
                                                    : `${item.document_name} — ${item.activity_type === 'comparison' ? 'comparison' : 'analysis'} failed`
                                                }
                                            </p>
                                            <small>
                                                {item.activity_type === 'comparison' && <span style={{color: '#6366f1', marginRight: '0.5rem', fontWeight: 600}}>Comparison</span>}
                                                {new Date(item.date).toLocaleString()}
                                            </small>
                                        </div>
                                    </div>
                                ))
                            )}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
