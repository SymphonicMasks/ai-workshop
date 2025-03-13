import {useEffect, useRef, useState} from "react";
import {Cursor, OpenSheetMusicDisplay as OSMD} from 'opensheetmusicdisplay';

function Sheets({data}) {
  const ref = useRef(null)

  const [osmd, setOsmd] = useState(null);

  useEffect(() => {

    const osmdInst = new OSMD(ref.current ?? '', {
      autoResize: true,
      drawTitle: false,
      newSystemFromXML: true,
      newSystemFromNewPageInXML: true,
      drawPartNames: false,
      drawPartAbbreviations: false,
      drawComposer: false,
      // cursorsOptions: [{type: 1, color: "#2bb8cd", alpha: 0.6, follow: true}], // highlight current measure instead of just a small vertical bar over approximate notes
      disableCursor: false,
    })
    setOsmd(osmdInst)
    osmdInst.load(data).then(() => {
      osmdInst.render()
      osmdInst.setLogLevel('info')
    });

  }, [])
  return (
    <>
      <button onClick={()=>{
        let cursorsOptions = [{type: 0, color: "#33e02f", alpha: 0.5, follow: true}, {type: 3, color: "#999999", alpha: 0.1, follow: false}];
        osmd.setOptions({cursorsOptions: cursorsOptions});
        osmd.enableOrDisableCursors(true);
        osmd.cursors[1].show();
      }}>sadf</button>
      <button onClick={()=>osmd.cursor.next()}>sadf</button>
      <div ref={ref}/>
    </>
  );
}

export default Sheets;
