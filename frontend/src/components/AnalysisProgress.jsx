import React from 'react';

/**
 * AnalysisProgress – step-by-step progress display during document analysis.
 *
 * Props:
 *   currentStepIndex – index (0-based) of the currently active step
 *   progressPercent  – 0-100 progress bar fill
 *   progressText     – status message displayed below the bar
 */

const STEPS = [
    { id: 'upload', icon: 'fa-upload', label: 'Upload' },
    { id: 'extract', icon: 'fa-file-alt', label: 'Extract & Segment' },
    { id: 'process', icon: 'fa-brain', label: 'AI Embeddings & NER' },
    { id: 'analyze', icon: 'fa-search', label: 'Contradiction Detection' },
    { id: 'report', icon: 'fa-chart-bar', label: 'Results' },
];

export default function AnalysisProgress({ currentStepIndex, progressPercent, progressText }) {
    return (
        <div className="analysis-progress">
            <div className="progress-card">
                <h3>Analyzing Documents</h3>

                <div className="progress-steps">
                    {STEPS.map((step, idx) => {
                        let className = 'progress-step';
                        if (idx < currentStepIndex) className += ' completed';
                        else if (idx === currentStepIndex) className += ' active';

                        return (
                            <div key={step.id} className={className} data-step={step.id}>
                                <i className={`fas ${step.icon}`}></i>
                                <span>{step.label}</span>
                            </div>
                        );
                    })}
                </div>

                <div className="progress-bar">
                    <div
                        className="progress-fill"
                        style={{ width: `${progressPercent}%` }}
                    ></div>
                </div>

                <div className="progress-text">{progressText}</div>
            </div>
        </div>
    );
}
