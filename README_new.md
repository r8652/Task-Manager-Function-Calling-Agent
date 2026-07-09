# Task Manager Agent

<div align="center">
  <img src="https://img.shields.io/badge/Python-3.10%2B-blue" alt="Python" />
  <img src="https://img.shields.io/badge/FastAPI-0.115%2B-009688" alt="FastAPI" />
  <img src="https://img.shields.io/badge/OpenAI-Function%20Calling-412991" alt="OpenAI" />
</div>

Task Manager Agent הוא פרויקט Python שמאפשר למשתמש לנהל משימות באמצעות שיחה טבעית עם AI. הפרויקט עושה שימוש ב-FastAPI וב-OpenAI Function Calling כדי להמיר בקשות של המשתמש לפעולות ממשיות על מערכת המשימות.

## ✨ מה הפרויקט עושה?

ה-Agent מסוגל:
- להוסיף משימות חדשות
- להציג משימות קיימות
- לעדכן משימות
- למחוק משימות

הכל דרך הודעה פשוטה כמו:
> "הוסף משימה חדשה בשם ללמוד FastAPI"

## 🧠 איך זה עובד?

1. המשתמש שולח הודעה ל-API.
2. ה-API מעביר את הבקשה ל-OpenAI עם פונקציות מוגדרות מראש.
3. OpenAI בוחר איזו פונקציה לבצע.
4. הפונקציה פועלת על שירות המשימות בזיכרון.
5. התוצאה מוחזרת למשתמש בתשובה טבעית.

## 🏗️ מבנה הפרויקט

```text
.
├── main.py
├── agent_service.py
├── todo_service.py
├── requirements.txt
├── .env.example
└── templates/
    └── index.html
```

## 🚀 התקנה

### 1) clone / פתח את הפרויקט

```bash
cd Function Calling Agent
```

### 2) צור סביבה וירטואלית

```bash
python -m venv .venv
```

### 3) הפעל את הסביבה

ב-Windows:

```bash
.venv\Scripts\activate
```

### 4) התקן את התלויות

```bash
pip install -r requirements.txt
```

### 5) הגדר את המפתח של OpenAI

העתיקו את הקובץ:

```bash
copy .env.example .env
```

ואז ערכו את ה-.env כך:

```env
OPENAI_API_KEY=your-openai-api-key
OPENAI_MODEL=gpt-4.1-mini
```

## ▶️ הרצת השרת

```bash
uvicorn main:app --reload
```

השרת יופעל בכתובת:

```text
http://127.0.0.1:8000
```

## 🌐 ממשק משתמש

הפרויקט כולל גם דף אינטרנט יפה ומעוצב שמאפשר להקליד הודעה ולשלוח אותה לא-Agent.

## 📡 Endpoint עיקרי

### POST /chat

שולח הודעה ל-Agent ומחזיר תגובה.

#### דוגמת בקשה

```bash
curl -X POST "http://127.0.0.1:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "הוסף משימה חדשה בשם ללמוד FastAPI"}'
```

#### דוגמת תגובה

```json
{
  "response": "הוספתי משימה חדשה בשם ללמוד FastAPI."
}
```

## 💡 דוגמאות לשאילתות

- הוסף משימה חדשה בשם "ללמוד FastAPI"
- הצג את כל המשימות שלי
- עדכן משימה לסטטוס הושלם
- מחק משימה מסוימת
- הצג רק משימות בעבודה

## ⚠️ הערות חשובות

- המשימות מאוחסנות בזיכרון בלבד (in-memory), ולכן הן יאבדו כאשר השרת יופעל מחדש.
- נדרש מפתח OpenAI תקף כדי שה-Agent יעבוד.

## 🛠️ טכנולוגיות בשימוש

- Python
- FastAPI
- OpenAI API
- Pydantic
- HTML/CSS/JavaScript
