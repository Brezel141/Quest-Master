# Quest Master 🐉

A gamified task management application that transforms your daily tasks into epic quests! Built with Flask and powered by AI assistance.

## 🎮 Features

### Current Features
- **Quest System**
  - Main Quests, Side Quests, and Sub-quests
  - Difficulty levels (Easy, Normal, Hard, Epic) with XP multipliers
  - Dynamic XP rewards based on quest type and difficulty
  - Progress tracking for quest chains

- **RPG Elements**
  - Level progression system with increasing XP requirements
  - Achievement badges for completing milestones
  - Daily streaks for consistent quest completion
  - Visual progress indicators

- **Organization**
  - Categories with custom colors and icons
  - Tag system for flexible quest organization
  - Priority levels (High, Medium, Low)
  - Quest templates for recurring tasks

- **User Interface**
  - Fantasy-themed design with medieval aesthetics
  - Responsive layout for all devices
  - Collapsible completed quests section
  - Interactive quest cards with hover effects

### 🚀 Planned Features
- Quest chains for sequential tasks
- Enhanced achievement system
- Theme customization
- Quest templates library
- Advanced statistics and analytics
- Time tracking for quests
- Quest comments and notes
- Custom categories and tag management
- Enhanced user profiles

## 🛠️ Technology Stack
- **Backend**: Python Flask
- **Database**: SQLAlchemy with SQLite
- **Frontend**: HTML, CSS, JavaScript
- **UI Framework**: Bootstrap 5
- **Icons**: Font Awesome
- **Authentication**: Flask-Login

## 🤝 Development Process
This project was developed through a collaborative effort between a human developer and an AI assistant (Claude). The development process showcased the potential of AI-assisted programming while addressing various challenges:

### Challenges & Solutions
1. **Database Structure**
   - Challenge: Designing a flexible schema for quest hierarchies
   - Solution: Implemented self-referential relationships for sub-quests

2. **XP System Balance**
   - Challenge: Creating a fair and engaging progression system
   - Solution: Implemented dynamic XP rewards with difficulty multipliers

3. **UI/UX Design**
   - Challenge: Creating an immersive fantasy theme
   - Solution: Custom CSS with medieval aesthetics and interactive elements

4. **Quest Management**
   - Challenge: Handling complex quest relationships
   - Solution: Developed a robust parent-child quest system

### AI Collaboration Highlights
- Rapid prototyping and implementation of features
- Real-time problem-solving and debugging
- Code optimization and best practices
- UI/UX improvements and suggestions
- Documentation and code organization

## 📝 Prerequisites
- Python 3.8+
- pip
- Virtual environment (recommended)

## 🚀 Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/quest-master.git
cd quest-master
```

2. Create and activate virtual environment:
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Unix/MacOS
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Initialize the database:
```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

5. Run the application:
```bash
flask run
```

## 🤝 Contributing
Contributions are welcome! Feel free to submit issues and enhancement requests.

## 📜 License
This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments
- Special thanks to Claude (Anthropic) for AI assistance
- Bootstrap team for the amazing UI framework
- Font Awesome for the iconic icons
- Flask team for the robust web framework

## 🎯 Project Status
The project is actively under development with new features being added regularly. Check the issues tab for planned enhancements and known bugs.

---
Built with ❤️ and 🤖 (Human + AI Collaboration)