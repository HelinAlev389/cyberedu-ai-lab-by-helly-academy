// src/components/LessonPresentation.jsx
import React, { useState } from 'react';

const LessonPresentation = ({ lessonSteps }) => {
  const [step, setStep] = useState(0);
  const [answers, setAnswers] = useState({});
  const [showFeedback, setShowFeedback] = useState(false);

  const current = lessonSteps[step];

  const handleNext = () => {
    if (current.type === 'question' && !answers[step]) {
      alert("Отговори на въпроса преди да продължиш.");
      return;
    }
    setShowFeedback(false);
    setStep(prev => Math.min(prev + 1, lessonSteps.length - 1));
  };

  const handleAnswer = (value) => {
    setAnswers(prev => ({ ...prev, [step]: value }));
    setShowFeedback(true); // тук в бъдеще ще викаме AI за оценка
  };

  return (
    <div className="lesson-container">
      <div className="step-content">
        {current.type === 'text' && (
          <div dangerouslySetInnerHTML={{ __html: current.content }} />
        )}
        {current.type === 'image' && <img src={current.src} alt="Илюстрация" />}
        {current.type === 'video' && (
          <iframe width="100%" height="315" src={current.src} frameBorder="0" allowFullScreen></iframe>
        )}
        {current.type === 'question' && (
          <div>
            <p><strong>{current.question}</strong></p>
            {current.options.map((opt, i) => (
              <button key={i} className="btn btn-outline-primary me-2" onClick={() => handleAnswer(opt)}>
                {opt}
              </button>
            ))}
            {showFeedback && <p className="mt-2 text-success">✅ Отговорът е запазен!</p>}
          </div>
        )}
      </div>

      <div className="step-controls mt-4">
        <button className="btn btn-secondary me-2" onClick={() => setStep(prev => Math.max(0, prev - 1))}>
          Назад
        </button>
        <button className="btn btn-primary" onClick={handleNext}>
          {step === lessonSteps.length - 1 ? 'Завърши урока' : 'Продължи'}
        </button>
      </div>
    </div>
  );
};

export default LessonPresentation;
