# Presentation Assets Library

This directory contains reusable assets for all PM Clinical Trials Agent presentations.

## Structure

```
assets/
├── images/
│   ├── logos/
│   ├── diagrams/
│   ├── screenshots/
│   └── icons/
├── videos/
│   ├── demos/
│   └── testimonials/
├── animations/
│   ├── transitions/
│   └── charts/
└── data-visualizations/
    ├── charts/
    └── interactive/
```

## Usage

Reference assets using relative paths:
```html
<img src="../assets/images/logos/company-logo.png" alt="Company Logo">
<video src="../assets/videos/demos/query-demo.mp4" controls></video>
```

## Asset Guidelines

- **Images**: PNG/JPG, optimized for web (<500KB)
- **Videos**: MP4 format, max 2 minutes, <10MB
- **Icons**: SVG format for scalability
- **Animations**: CSS/JS based, smooth 60fps