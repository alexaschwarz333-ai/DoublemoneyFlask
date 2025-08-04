# DoubleMoney Investment Platform

## Overview

DoubleMoney is a Flask-based investment platform that allows users to double their cryptocurrency investments in 7 days. The platform supports USDC (ERC20) and USDT (TRC20) investments with a multi-tier referral system. It features both user-facing functionality and an administrative dashboard for managing investments, users, and platform settings.

**Recent Changes (August 4, 2025):**
- **COMPLETE PROJECT CLEANUP**: Removed all Laravel/PHP related files, archives, and templates
- **Pure Flask Structure**: Project contains only Flask core components
- **Clean Templates**: Removed Laravel templates, kept only Flask HTML templates
- **Optimized Architecture**: Minimal, focused Flask setup
- **Development Ready**: Pure Flask with PostgreSQL, no mixed frameworks

## User Preferences

Preferred communication style: Simple, everyday language.
Don't overdo features - keep it simple and functional.

## System Architecture

### Backend Architecture
- **Framework**: Laravel 11 with Eloquent ORM (doublemoney-laravel/)
- **Database**: PostgreSQL (configured for development and production)
- **Session Management**: Laravel sessions with database storage
- **Authentication**: Laravel's built-in authentication with custom middleware
- **Task Scheduling**: Laravel scheduler for background processing
- **Implementation**: Complete Laravel/PHP system with MVC architecture
- **Original Flask**: Maintained alongside Laravel (separate implementation)

### Frontend Architecture
- **Template Engine**: Jinja2 with Flask
- **CSS Framework**: Bootstrap 5 with dark theme
- **JavaScript**: Vanilla JS with modular class-based architecture
- **Icons**: Font Awesome 6.4.0
- **Charts**: Chart.js for admin analytics

### Data Storage Solutions
- **Primary Database**: PostgreSQL with Laravel Eloquent models
- **Session Storage**: Laravel session management
- **Configuration**: Laravel .env configuration with fallback defaults
- **Migrations**: Laravel database migrations for schema management
- **Seeders**: Database seeders for initial data population

## Key Components

### User Management System
- **Registration**: Phone-based authentication with country code support
- **Login/Logout**: Session-based authentication
- **Referral System**: Multi-tier percentage-based referrals (3% to 25%)
- **User Profiles**: Phone numbers, withdrawal wallets, referral codes

### Investment System
- **Investment Plans**: Fixed 7-day doubling plan ($100-$100,000)
- **Supported Currencies**: USDC (ERC20) and USDT (TRC20)
- **Status Tracking**: Pending → Confirmed → Completed workflow
- **Timer System**: Real-time countdown for investment completion

### Admin Panel
- **Dashboard**: Statistics and analytics overview
- **User Management**: View, edit, and manage user accounts
- **Investment Management**: Approve, track, and manage investments
- **Wallet Management**: Configure deposit/withdrawal addresses
- **Settings Management**: Platform configuration and social links

### Referral System
- **Tier Structure**: 5 levels based on active referrals
- **Earning Calculation**: Percentage-based on referred user investments
- **Payout Tracking**: Pending and paid earnings management

## Data Flow

### Investment Flow
1. User registers with phone number and optional referral code
2. User makes investment deposit (USDC/USDT)
3. Admin confirms investment through admin panel
4. Investment runs for 7 days with real-time timer
5. System automatically marks investment as completed
6. Referral earnings calculated and distributed

### Referral Flow
1. User shares referral code with others
2. New users register using referral code
3. When referred user makes confirmed investment, referrer earns percentage
4. Earnings tracked as pending until payout date
5. Admin processes referral payouts

### Admin Management Flow
1. Admin logs in through separate admin interface
2. Reviews pending investments and user registrations
3. Confirms legitimate investments
4. Monitors platform statistics and user activity
5. Manages platform settings and wallet addresses

## External Dependencies

### Frontend Libraries
- **Bootstrap 5**: UI framework with dark theme
- **Font Awesome 6.4.0**: Icon library
- **Chart.js**: Admin dashboard analytics
- **Flag Icons CSS**: Country flag display

### Backend Libraries
- **Flask**: Web framework
- **SQLAlchemy**: Database ORM
- **Werkzeug**: Security utilities
- **APScheduler**: Background task scheduling

### Infrastructure
- **MySQL**: Primary database
- **ProxyFix**: Reverse proxy support for deployment

## Deployment Strategy

### Environment Configuration
- **Development**: SQLite fallback with debug mode
- **Production**: MySQL with environment variable configuration
- **Session Security**: Environment-based secret key management

### Database Setup
- **Models**: User, Admin, Investment, Wallet, ReferralEarning, Settings
- **Migrations**: Manual SQL schema deployment
- **Connection Pooling**: Configured for production stability

### Security Considerations
- **Password Hashing**: Werkzeug security functions
- **Session Management**: Server-side session storage
- **Admin Authentication**: Separate admin login system
- **Input Validation**: Form validation and sanitization

### Internationalization
- **Multi-language Support**: Translation system with session-based language selection
- **Supported Languages**: English as primary, extensible translation system
- **Currency Display**: USD-based with proper formatting

The platform is designed as a complete investment management system with separate user and admin interfaces, real-time investment tracking, and a sophisticated referral program. The architecture supports both development and production deployments with MySQL database integration.