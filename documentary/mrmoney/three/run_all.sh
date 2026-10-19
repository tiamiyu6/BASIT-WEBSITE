#!/bin/bash
# render every 3D shot (resumable). usage: three/run_all.sh OUT_ROOT   (from documentary/mrmoney)
R=$1
go() { n="$1"; d="$2"; shift 2; t=$(date +%s); python3 three/shots.py "$n" "$R/$d" "$@" > "$R/$d.log" 2>&1; echo "$d $(ls "$R/$d" | wc -l) frames $(( $(date +%s)-t ))s"; }
go mm mm
go phone phone
go slips slips
go chapter ch_OLOLADE OLOLADE gold
go chapter ch_GIRAN GIRAN red
go chapter ch_ILE-IFE ILE-IFE gold
go chapter ch_2022 2022 gold
go chapter ch_BRIXTON BRIXTON white
go chapter "ch_WORK OF ART" "WORK OF ART" gold
go chapter "ch_LUNGU BOY" "LUNGU BOY" gold
go chapter "ch_WHY LOVE" "WHY LOVE" red
go chapter 'ch_M$NEY' 'M$NEY' gold
go chapter "ch_THE VIBE" "THE VIBE" gold
go passport passport
go vinyl vinyl
go candles candles
go naira naira
go mic mic
echo ALL3D DONE
