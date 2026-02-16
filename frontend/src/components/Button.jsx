import React from 'react';

/**
 * Button – reusable button primitive.
 *
 * Props:
 *   variant   – 'primary' | 'secondary' | 'ghost' (default: 'primary')
 *   size      – 'sm' | 'md' | 'lg' (default: 'md')
 *   loading   – boolean, shows spinner and disables
 *   icon      – optional Font Awesome class (e.g. 'fas fa-play')
 *   children  – button label
 *   ...rest   – forwarded to <button>
 */
export default function Button({
    variant = 'primary',
    size = 'md',
    loading = false,
    icon,
    children,
    className = '',
    disabled,
    ...rest
}) {
    const classes = [
        'btn',
        `btn--${variant}`,
        `btn--${size}`,
        loading ? 'btn--loading' : '',
        className,
    ]
        .filter(Boolean)
        .join(' ');

    return (
        <button className={classes} disabled={disabled || loading} {...rest}>
            {loading ? (
                <span className="btn-spinner"></span>
            ) : (
                icon && <i className={icon}></i>
            )}
            <span>{children}</span>
        </button>
    );
}
