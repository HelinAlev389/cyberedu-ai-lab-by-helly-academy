// src/pages/LessonPage.jsx
import React from 'react';
import LessonPresentation from '../components/LessonPresentation';

const lessonSteps = [
  { type: "text", content: "<h2>🔐 Основи на мрежова сигурност</h2><p>Ще научим какво е IP, firewall и други.</p>" },
  { type: "image", src: "/static/uploads/firewall-diagram.png" },
  { type: "video", src: "https://www.youtube.com/embed/dQw4w9WgXcQ" },
  {
    type: "question",
    question: "Какво е IP адрес?",
    options: ["Уникален номер в мрежата", "Парола", "MAC адрес"]
  },
  { type: "text", content: "<p>IP адресът е като адрес на твоя компютър в интернет.</p>" }
];

export default function LessonPage() {
  return (
    <div className="container">
      <LessonPresentation lessonSteps={lessonSteps} />
    </div>
  );
}
