import useAutoScroll from '../hooks/useAutoScroll';
import Spinner from './Spinner';
import userIcon from '../assets/images/user.svg';
import errorIcon from '../assets/images/error.svg';
import Sheets from "./Sheets.jsx";

function ChatMessages({ messages, isLoading }) {
  const scrollContentRef = useAutoScroll(isLoading);

  return (
    <div ref={scrollContentRef} className='grow space-y-4'>
      {messages.map(({ role, content, url, loading, isError, xml, errors}, idx) => (
        <div key={idx} className={`flex items-start gap-4 py-4 px-3 rounded-xl ${role === 'user' ? 'bg-primary-blue/10' : ''}`}>
          {role === 'user' && (
            <img
              className='h-[26px] w-[26px] shrink-0'
              src={userIcon}
              alt='user'
            />
          )}
          <div className={'w-full'}>
            {!isError && <div className='markdown-container'>
              {(loading && !content) ? <Spinner />
                : (role === 'assistant')
                  ? <Sheets data={xml} errors={errors} content={content}/>
                  : <audio style={{width: '100%'}} src={url} controls={true} controlsList={"nodownload"}/>
              }
            </div>}
            {isError && (
              <div className={`flex items-center gap-1 text-sm text-error-red ${content && 'mt-2'}`}>
                <img className='h-5 w-5' src={errorIcon} alt='error' />
                <span>{content}</span>
              </div>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}

export default ChatMessages;
