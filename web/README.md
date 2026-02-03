# Portfolio Website

A modern, responsive portfolio website built with Svelte and Tailwind CSS.

## Features

- **Home section** with hero image, name, title, and call-to-action buttons
- **About section** with personal information and skills
- **Projects section** showcasing 6 different projects with descriptions and technologies
- **Contact section** with email, phone, and social media links
- **Responsive design** that works on desktop, tablet, and mobile devices
- **Modern UI** with smooth animations and transitions
- **Dark theme** with vibrant accent colors

## Tech Stack

- [Svelte 5](https://svelte.dev/) - Frontend framework
- [Tailwind CSS](https://tailwindcss.com/) - Utility-first CSS framework
- [Vite](https://vitejs.dev/) - Build tool and development server

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/JRone-git/HelpMate.git
   cd HelpMate/web
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm run dev
   ```

4. Open your browser and navigate to `http://localhost:3000`

## Building for Production

To build the project for production:

```bash
npm run build
```

This will create a `dist` folder with the optimized production files.

## Previewing Production Build

To preview the production build locally:

```bash
npm run preview
```

## Project Structure

```
web/
├── src/
│   ├── components/
│   │   ├── Layout.svelte     # Main layout component
│   │   ├── Skills.svelte     # Skills section component
│   │   └── ...
│   ├── main.svelte          # App entry point
│   └── styles/
├── package.json
├── vite.config.js
└── README.md
```

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## License

This project is open source and available under the [MIT License](LICENSE).