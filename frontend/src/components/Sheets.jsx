import {useEffect, useRef, useState} from "react";
import * as vexml from '@stringsync/vexml';
import deleteIcon from "@/assets/images/delete.svg";
import {AudioRecorder} from "react-audio-voice-recorder";
import sendIcon from "@/assets/images/send.svg";
import directionIcon from "@/assets/images/next-icon.svg"


function Sheets({data}) {
    const ref = useRef(null)
    const div = ref.current

    const rendererRef = useRef(null);

    const [score, setScore] = useState(null);
    const [cursor, setCursor] = useState(null);

    const fragmentCursor = useRef(null);
    const fragmentWidth = 200;

    const [currentError, setCurrentError] = useState(3);


    const toNextError = () => {
        cursor.next();
        // cursor.goTo();
    }

    const toPreviousError = () => {
        cursor.previous();
    }


    useEffect(() => {
        const score = vexml.renderMusicXML(data, ref.current);
        setScore(score);

        // Add
        const cursorModel = score.addCursor();
        setCursor(cursorModel);

        // Render
        const cursorComponent = vexml.SimpleCursor.render(score.getOverlayElement());

        console.log(score.getMeasures()[3].getFragments()[0].getParts()[0].getStaves()[0].getVoices()[0].getEntries()[0]);
        const rect = cursorModel.getState().cursorRect.toRectLike()
        cursorComponent.update({...rect, w: 500, x: 200})
        // Listen
        cursorModel.addEventListener(
            'change',
            (e) => {
                const rect = score.getMeasures()[e.index].rect()
                cursorComponent.update(rect);

                const cursor = document.querySelector('.vexml-cursor')
                // cursor.update({...e.cursorRect});
                console.log(e, cursor)
                // The model infers its visibility via the cursorRect. It assumes you've updated appropriately.
                cursor.scrollIntoView({
                    block: 'center',
                    inline: 'center',
                    behavior: 'smooth'
                });
            },
            {emitBootstrapEvent: true}
        );
    }, [])

    return (
        <>
        <div className='p-1.5 bg-primary-blue/35 rounded-[30px] z-50 font-mono origin-bottom animate-chat duration-400'>
            <div className='px-3 bg-white relative shrink-0 rounded-3xl overflow-hidden ring-primary-blue ring-1 focus-within:ring-2 transition-all h-[60px] flex flex-nowrap items-center gap-2'>
              <button
                className='w-[30px] h-[30px] p-1 rounded-md hover:bg-primary-blue/20 flex-shrink-0 rotate-180'
                onClick={toPreviousError}
              >
                <img src={directionIcon} alt='delete' className='w-[22px] h-[22px]'/>
              </button>


              <div  className="w-full h-full flex flex-nowrap items-center justify-center">
В IT, как и в драке, главное — не скорость, а точность. Один точный удар — и всё падает.              </div>

                <button
                className='w-[30px] h-[30px] p-1 rounded-md hover:bg-primary-blue/20 flex-shrink-0'
                onClick={toNextError}
              >
                <img src={directionIcon} alt='send' />
              </button>


            </div>
          </div>
            <div ref={ref}/>
        </>
    );
}

export default Sheets;
