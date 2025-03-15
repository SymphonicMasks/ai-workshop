import {useEffect, useRef, useState} from "react";
import * as vexml from '@stringsync/vexml';
import directionIcon from "../assets/images/next-icon.svg"

function Sheets({data, errors, content}) {
    const ref = useRef(null)

    const [score, setScore] = useState(null);
    const [cursor, setCursor] = useState(null);

    const [index, setIndex] = useState();

    const error = Number.isInteger(index)  ? errors.wrong_parts[index] : undefined;


    const toNextError = () => {
        cursor.next();
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

        const rect = cursorModel.getState().cursorRect.toRectLike()
        cursorComponent.update({...rect, w: 500, x: 200})
        // Listen
        cursorModel.addEventListener(
            'change',
            (e) => {
                const part = errors.wrong_parts[e.index].tact_index
                setIndex(e.index)
                const rect = score.getMeasures()[part].rect();
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
                  {error ? error.feedback : ''}
              </div>

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
