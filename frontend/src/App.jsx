import Chatbot from '@/components/Chatbot';

function App() {

  return (
    <div className='flex flex-col min-h-full w-full mx-auto px-4'>
      <header className='sticky top-0 shrink-0 z-20 bg-white'>
        <div className='flex flex-col h-full content-center gap-1 pt-4 pb-2 flex-wrap'>
          <h1 className='font-urbanist text-[1.65rem] font-semibold'>Symphonic masks</h1>
        </div>
      </header>
      <Chatbot />
    </div>
  );
}

export default App;
