import { useState } from 'react';
import { useImmer } from 'use-immer';
import api from '@/api';
import { parseSSEStream } from '@/utils';
import ChatMessages from '@/components/ChatMessages';
import ChatInput from '@/components/ChatInput';

function Chatbot() {
  const [chatId, setChatId] = useState(null);
  const [messages, setMessages] = useImmer([]);

  const isLoading = messages.length && messages[messages.length - 1].loading;

  async function submitNewMessage(record) {
    if (isLoading) return;

    setMessages(draft => [...draft,
      { role: 'user', record: record, url: URL.createObjectURL(record) },
      { role: 'assistant', content: '', xml: '', errors: [], loading: true }
    ]);

    try {
      // 1. Отправляем аудио на обработку
      const formData = new FormData();
      formData.append('audio', record, 'recording.wav');
      
      const feedbackRes = await fetch('http://127.0.0.1:8081/feedback', {
        method: 'POST',
        body: formData
      });
      
      if (!feedbackRes.ok) throw new Error('Feedback request failed');
      const { filename } = await feedbackRes.json();

      // 2. Получаем сгенерированный XML
      const vizRes = await fetch(`http://127.0.0.1:8081/visualization/${filename}`);
      if (!vizRes.ok) throw new Error('Visualization request failed');
      const xmlData = await vizRes.text();

      // 3. Обновляем состояние с полученными данными
      setMessages(draft => {
        const index = draft.length - 1;
        draft[index] = {
          ...draft[index],
          content: 'Анализ вашего исполнения',
          xml: xmlData,
          loading: false
        };
      });

    } catch (err) {
      setMessages(draft => {
        const index = draft.length - 1;
        draft[index] = {
          ...draft[index],
          error: true,
          loading: false,
          content: 'Ошибка при обработке аудио'
        };
      });
    }
  }

  return (
    <div className='relative grow flex flex-col gap-6 pt-6'>
      <form className="max-w-sm w-full mx-auto">
        <label htmlFor="countries" className="block mb-2 text-sm font-medium text-gray-900 dark:text-white">Выбери трек
        </label>
        <div className='p-0.5 bg-primary-blue/35 rounded-[10px] z-50 font-mono origin-bottom animate-chat duration-400'>
          <select id="countries"
                  className="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500">
            <option selected>Выбери трек</option>
            <option value="US">United States</option>
            <option value="CA">Canada</option>
            <option value="FR">France</option>
            <option value="DE">Germany</option>
          </select>
        </div>


      </form>
      <ChatMessages
        messages={messages}
        isLoading={isLoading}
      />
      <ChatInput
        submitNewMessage={submitNewMessage}
      />
    </div>
  );
}

export default Chatbot;
