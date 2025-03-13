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

    // const imitateRequest = new Promise(resolve => {
    //   setTimeout(()=>{
    //     resolve
    //   }, 1000)
    // })

    fetch('violin.xml').then(data => data.text()).then((data)=>{

      setTimeout(()=>{

        try {
          setMessages(draft => {
            const index = draft.length - 1
            draft[index] = {
              ...draft[index],
              content: 'Какой-то отзыв об игре',
              xml: data,
              result: [
                {
                  original_note: 'A',
                  played_note: "D",
                  status: "wrong",
                  original_duration: '0.8',
                  played_duration: '1',
                  tact_number: 5,
                  start_time: 12.6,
                  end_time: 14.6
                }
              ],
              loading: true
            };

            draft[draft.length - 1].loading = false;
          });
        } catch (err) {
          setMessages(draft => {
            draft[draft.length - 1].loading = false;
            draft[draft.length - 1].error = true;
          });
        }
      }, 1000)

    })
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
