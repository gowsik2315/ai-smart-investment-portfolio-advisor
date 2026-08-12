# Smart Investment Advisor - Frontend

React frontend for the AI-Powered Smart Investment Portfolio Advisor.

## Setup Instructions

### 1. Install Dependencies

```bash
npm install
```

### 2. Configure Environment Variables

```bash
# Copy example environment file
copy .env.example .env  # Windows
# cp .env.example .env  # macOS/Linux

# Edit .env file if needed (default values should work for local development)
```

### 3. Start Development Server

```bash
npm start
```

The application will be available at http://localhost:3000

## Available Scripts

### `npm start`
Runs the app in development mode.

### `npm build`
Builds the app for production to the `build` folder.

### `npm test`
Launches the test runner in interactive watch mode.

## Project Structure

```
frontend/
├── public/               # Static files
├── src/
│   ├── components/      # Reusable components
│   │   ├── Layout/      # Layout components
│   │   └── common/      # Common components
│   ├── pages/           # Page components
│   ├── services/        # API services
│   ├── context/         # React context
│   ├── hooks/           # Custom hooks (Phase 2)
│   ├── utils/           # Utility functions (Phase 2)
│   ├── App.js           # Main app component
│   ├── index.js         # Application entry point
│   └── index.css        # Global styles
├── package.json         # Dependencies
└── tailwind.config.js   # Tailwind configuration
```

## Pages

- **Home** - Landing page with feature overview
- **Login** - User authentication
- **Register** - User registration
- **Dashboard** - Main dashboard (Placeholder)
- **Financial Profile** - Financial information form (Placeholder)
- **Risk Assessment** - Risk profiling questionnaire (Placeholder)
- **Portfolio** - Portfolio management (Placeholder)
- **SIP Planner** - SIP planning and simulation (Placeholder)

## Components

### Layout Components
- **Layout** - Main layout wrapper
- **Navbar** - Navigation bar
- **Footer** - Application footer

### Common Components
- **Card** - Reusable card container
- **Button** - Button with variants
- **Input** - Form input field
- **Loading** - Loading spinner

## Styling

This project uses **Tailwind CSS** for styling with custom configuration:

- Custom color palette (primary, secondary)
- Custom utilities for scrollbars
- Reusable component classes (btn, input, card, badge)

## API Integration

API calls are centralized in the `services/` directory:

- **api.js** - Axios configuration and interceptors
- **authService.js** - Authentication API calls
- **profileService.js** - Profile API calls

## State Management

- **AuthContext** - Global authentication state

## Environment Variables

```
REACT_APP_API_BASE_URL=http://localhost:8000
REACT_APP_API_TIMEOUT=10000
REACT_APP_NAME=Smart Investment Portfolio Advisor
REACT_APP_VERSION=1.0.0
```

## Notes

- Phase 1 includes basic UI and authentication flow
- Placeholder pages will be implemented in Phase 2
- All pages are responsive and mobile-friendly
- Dark mode support can be added in future phases
