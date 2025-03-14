import sendIcon from '../assets/images/send.svg';
import deleteIcon from '../assets/images/delete.svg';
import {AudioRecorder, useAudioRecorder} from 'react-audio-voice-recorder';
import {useState} from "react";
import './ChatInput.css'
//...

function ChatInput({submitNewMessage}) {
  const [record, setRecord] = useState(null);
  const [url, setUrl] = useState(null);

  const recorderControls = useAudioRecorder(
    {
      noiseSuppression: false,
      echoCancellation: false,
    },
    (err) => console.table(err) // onNotAllowedOrFound
  );


  const onRecordingComplete = (blob) => {
    setRecord(blob)
    setUrl(URL.createObjectURL(blob))
  }

  const onDeleteRecord = () => {
    setRecord(null)
    setUrl(null)
  }

  const onSendRequest = () => {
    submitNewMessage(record);
    onDeleteRecord()
  }

  return(
    <div className='sticky bottom-0 bg-white py-4'>
      <div className='p-1.5 bg-primary-blue/35 rounded-[30px] z-50 font-mono origin-bottom animate-chat duration-400'>
        <div className='px-3 bg-white relative shrink-0 rounded-3xl overflow-hidden ring-primary-blue ring-1 focus-within:ring-2 transition-all h-[60px] flex flex-nowrap items-center gap-2'>
          {url && <button
            className='w-[30px] h-[30px] p-1 rounded-md hover:bg-primary-blue/20 flex-shrink-0'
            onClick={onDeleteRecord}
          >
            <img src={deleteIcon} alt='delete' className='w-[22px] h-[22px]'/>
          </button>}


          <div style={{display: url ? '' : 'none'}} className="w-full h-full flex flex-nowrap items-center justify-center">
            <audio src={url} controls={true}/>
          </div>

          <div style={{display: url ? 'none' : ''}} className="w-full h-full flex flex-nowrap items-center justify-center">
              <AudioRecorder
                onRecordingComplete={onRecordingComplete}
                recorderControls={recorderControls}
                showVisualizer={true}
              />
          </div>

          {url &&
            <button
            className='w-[30px] h-[30px] p-1 rounded-md hover:bg-primary-blue/20 flex-shrink-0'
            onClick={onSendRequest}
          >
            <img src={sendIcon} alt='send' />
          </button>
          }

        </div>
      </div>
    </div>
  );
}

export default ChatInput;
