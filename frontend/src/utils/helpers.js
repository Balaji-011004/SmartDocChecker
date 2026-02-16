/**
 * Format file size in bytes to a human-readable string.
 */
export function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

/**
 * Check if a file has a valid document type.
 */
export function isValidFile(file) {
    const validTypes = [
        'application/pdf',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'text/plain',
    ];
    return (
        validTypes.includes(file.type) ||
        file.name.toLowerCase().endsWith('.pdf') ||
        file.name.toLowerCase().endsWith('.docx') ||
        file.name.toLowerCase().endsWith('.txt')
    );
}

/**
 * Return a Font Awesome icon class based on file type.
 */
export function getFileIcon(file) {
    if (file.type.includes('pdf')) return 'fa-file-pdf';
    if (file.type.includes('word')) return 'fa-file-word';
    if (file.type.includes('text')) return 'fa-file-alt';
    return 'fa-file';
}

/**
 * Validate a URL string.
 */
export function isValidUrl(string) {
    try {
        new URL(string);
        return true;
    } catch (_) {
        return false;
    }
}

/**
 * Return colors for contradiction type badges (used in PDF report).
 */
export function getTypeColor(type) {
    const colors = {
        temporal: { bg: [254, 243, 199], text: [146, 64, 14] },
        date: { bg: [254, 243, 199], text: [146, 64, 14] },
        numerical: { bg: [219, 234, 254], text: [29, 78, 216] },
        numeric: { bg: [219, 234, 254], text: [29, 78, 216] },
        quantity: { bg: [219, 234, 254], text: [29, 78, 216] },
        financial: { bg: [209, 250, 229], text: [6, 95, 70] },
        requirement: { bg: [252, 231, 243], text: [190, 24, 93] },
        modal: { bg: [252, 231, 243], text: [190, 24, 93] },
        authority: { bg: [243, 232, 255], text: [109, 40, 217] },
        entity: { bg: [255, 237, 213], text: [194, 65, 12] },
        location: { bg: [204, 251, 241], text: [15, 118, 110] },
        semantic: { bg: [209, 250, 229], text: [6, 95, 70] },
    };
    return colors[type] || colors.semantic;
}

/**
 * Return colors for severity badges (used in PDF report).
 */
export function getSeverityColor(severity) {
    const colors = {
        high: { bg: [254, 226, 226], text: [220, 38, 38] },
        medium: { bg: [254, 243, 199], text: [217, 119, 6] },
        low: { bg: [224, 242, 254], text: [3, 105, 161] },
    };
    return colors[severity] || colors.medium;
}

/**
 * Return a Font Awesome icon class for a notification type.
 */
export function getNotificationIcon(type) {
    switch (type) {
        case 'success':
            return 'fa-check-circle';
        case 'error':
            return 'fa-exclamation-circle';
        case 'warning':
            return 'fa-exclamation-triangle';
        default:
            return 'fa-info-circle';
    }
}

/**
 * Return a background color for a notification type.
 */
export function getNotificationColor(type) {
    switch (type) {
        case 'success':
            return '#10b981';
        case 'error':
            return '#ef4444';
        case 'warning':
            return '#f59e0b';
        default:
            return '#2563eb';
    }
}
