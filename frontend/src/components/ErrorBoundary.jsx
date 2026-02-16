import React from 'react';

/**
 * ErrorBoundary – catches JS errors in the component tree and shows
 * a friendly fallback UI instead of a white screen.
 */
export default class ErrorBoundary extends React.Component {
    constructor(props) {
        super(props);
        this.state = { hasError: false, error: null };
    }

    static getDerivedStateFromError(error) {
        return { hasError: true, error };
    }

    componentDidCatch(error, errorInfo) {
        console.error('[ErrorBoundary] Caught error:', error, errorInfo);
    }

    handleReset = () => {
        this.setState({ hasError: false, error: null });
    };

    render() {
        if (this.state.hasError) {
            return (
                <div style={{
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center',
                    justifyContent: 'center',
                    minHeight: '60vh',
                    padding: '2rem',
                    textAlign: 'center',
                    fontFamily: 'Inter, system-ui, sans-serif',
                }}>
                    <div style={{
                        background: '#fef2f2',
                        border: '1px solid #fecaca',
                        borderRadius: '12px',
                        padding: '2rem 3rem',
                        maxWidth: '500px',
                    }}>
                        <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>⚠️</div>
                        <h2 style={{ color: '#991b1b', margin: '0 0 0.5rem' }}>
                            Something went wrong
                        </h2>
                        <p style={{ color: '#7f1d1d', fontSize: '0.95rem', margin: '0 0 1.5rem' }}>
                            An unexpected error occurred. Please try again.
                        </p>
                        {this.state.error && (
                            <details style={{ textAlign: 'left', marginBottom: '1rem', fontSize: '0.85rem', color: '#6b7280' }}>
                                <summary style={{ cursor: 'pointer' }}>Error details</summary>
                                <pre style={{ whiteSpace: 'pre-wrap', wordBreak: 'break-word', marginTop: '0.5rem' }}>
                                    {this.state.error.toString()}
                                </pre>
                            </details>
                        )}
                        <button
                            onClick={this.handleReset}
                            style={{
                                background: '#dc2626',
                                color: 'white',
                                border: 'none',
                                borderRadius: '8px',
                                padding: '0.6rem 1.5rem',
                                fontSize: '0.95rem',
                                cursor: 'pointer',
                                fontWeight: '500',
                            }}
                        >
                            Try Again
                        </button>
                    </div>
                </div>
            );
        }

        return this.props.children;
    }
}
