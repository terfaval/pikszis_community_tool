-- 2025-08-23_add_new_qtypes.sql
do $$ begin
  -- új nyílt típusok
  alter type q_type add value if not exists 'open_long';
  alter type q_type add value if not exists 'open_short';
  alter type q_type add value if not exists 'open_multiple';
  -- slider/ratings alternatívák (opcionális most)
  alter type q_type add value if not exists 'likert_slider_1_5';
  alter type q_type add value if not exists 'likert_slider_1_4';
  alter type q_type add value if not exists 'rating_stars_1_5';
exception when duplicate_object then null;
end $$;

-- opcionális: questions táblában paraméterek az open_multiple és sliderhez
alter table if exists questions
  add column if not exists ui_params jsonb;  -- pl. {"count":3} open_multiple-hoz, {"min":1,"max":5} sliderhez
