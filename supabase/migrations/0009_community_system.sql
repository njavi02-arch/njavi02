-- COMMUNITY SYSTEM: Posts, Comments, Likes, Hashtags
-- Allows users to create content, discover communities by interests/hashtags

-- Hashtags/Tags table
create table if not exists hashtags (
  id uuid primary key default gen_random_uuid(),
  name text not null unique,
  category text not null,
  description text,
  created_at timestamp with time zone default now()
);

-- Posts table
create table if not exists posts (
  id uuid primary key default gen_random_uuid(),
  author_id uuid not null references profiles(id) on delete cascade,
  content text not null,
  media_urls text[], -- Array of photo URLs from storage
  likes_count int default 0,
  comments_count int default 0,
  shares_count int default 0,
  is_archived boolean default false,
  created_at timestamp with time zone default now(),
  updated_at timestamp with time zone default now()
);

-- Post-Hashtag junction table
create table if not exists post_hashtags (
  post_id uuid not null references posts(id) on delete cascade,
  hashtag_id uuid not null references hashtags(id) on delete cascade,
  primary key (post_id, hashtag_id)
);

-- Comments on posts
create table if not exists comments (
  id uuid primary key default gen_random_uuid(),
  post_id uuid not null references posts(id) on delete cascade,
  author_id uuid not null references profiles(id) on delete cascade,
  content text not null,
  likes_count int default 0,
  created_at timestamp with time zone default now(),
  updated_at timestamp with time zone default now()
);

-- Likes on posts
create table if not exists post_likes (
  id uuid primary key default gen_random_uuid(),
  post_id uuid not null references posts(id) on delete cascade,
  liker_id uuid not null references profiles(id) on delete cascade,
  created_at timestamp with time zone default now(),
  unique(post_id, liker_id) -- One like per user per post
);

-- Likes on comments
create table if not exists comment_likes (
  id uuid primary key default gen_random_uuid(),
  comment_id uuid not null references comments(id) on delete cascade,
  liker_id uuid not null references profiles(id) on delete cascade,
  created_at timestamp with time zone default now(),
  unique(comment_id, liker_id)
);

-- User follows hashtags/interests
create table if not exists hashtag_followers (
  user_id uuid not null references profiles(id) on delete cascade,
  hashtag_id uuid not null references hashtags(id) on delete cascade,
  created_at timestamp with time zone default now(),
  primary key (user_id, hashtag_id)
);

-- Icebreaker phrases (dynamic starting messages)
create table if not exists icebreaker_packs (
  id uuid primary key default gen_random_uuid(),
  pack_number int not null unique,
  phrases text[] not null, -- Array of starter phrases
  created_at timestamp with time zone default now()
);

-- Track user interactions count (for pack rotation)
create table if not exists interaction_tracking (
  user_id uuid primary key references profiles(id) on delete cascade,
  total_interactions int default 0,
  current_pack int default 1,
  last_pack_rotation timestamp with time zone default now()
);

-- Enable RLS
alter table hashtags enable row level security;
alter table posts enable row level security;
alter table post_hashtags enable row level security;
alter table comments enable row level security;
alter table post_likes enable row level security;
alter table comment_likes enable row level security;
alter table hashtag_followers enable row level security;
alter table icebreaker_packs enable row level security;
alter table interaction_tracking enable row level security;

-- RLS Policies for hashtags (everyone can read)
create policy hashtags_select_all on hashtags
  for select to authenticated
  using (true);

-- RLS Policies for posts
create policy posts_select_all on posts
  for select to authenticated
  using (not is_archived and author_id not in (
    select blocked_id from blocks where blocker_id = auth.uid()
    union
    select blocker_id from blocks where blocked_id = auth.uid()
  ));

create policy posts_insert_own on posts
  for insert to authenticated
  with check (author_id = auth.uid());

create policy posts_update_own on posts
  for update to authenticated
  using (author_id = auth.uid())
  with check (author_id = auth.uid());

create policy posts_delete_own on posts
  for delete to authenticated
  using (author_id = auth.uid());

-- RLS for post_hashtags
create policy post_hashtags_select_all on post_hashtags
  for select to authenticated
  using (post_id in (select id from posts));

create policy post_hashtags_insert_own on post_hashtags
  for insert to authenticated
  with check (post_id in (select id from posts where author_id = auth.uid()));

-- RLS for comments
create policy comments_select_all on comments
  for select to authenticated
  using (post_id in (select id from posts) and author_id not in (
    select blocked_id from blocks where blocker_id = auth.uid()
    union
    select blocker_id from blocks where blocked_id = auth.uid()
  ));

create policy comments_insert_own on comments
  for insert to authenticated
  with check (author_id = auth.uid());

create policy comments_update_own on comments
  for update to authenticated
  using (author_id = auth.uid());

create policy comments_delete_own on comments
  for delete to authenticated
  using (author_id = auth.uid());

-- RLS for post_likes
create policy post_likes_select_all on post_likes
  for select to authenticated
  using (true);

create policy post_likes_insert_own on post_likes
  for insert to authenticated
  with check (liker_id = auth.uid());

create policy post_likes_delete_own on post_likes
  for delete to authenticated
  using (liker_id = auth.uid());

-- RLS for comment_likes
create policy comment_likes_select_all on comment_likes
  for select to authenticated
  using (true);

create policy comment_likes_insert_own on comment_likes
  for insert to authenticated
  with check (liker_id = auth.uid());

create policy comment_likes_delete_own on comment_likes
  for delete to authenticated
  using (liker_id = auth.uid());

-- RLS for hashtag_followers
create policy hashtag_followers_select_own on hashtag_followers
  for select to authenticated
  using (user_id = auth.uid());

create policy hashtag_followers_insert_own on hashtag_followers
  for insert to authenticated
  with check (user_id = auth.uid());

create policy hashtag_followers_delete_own on hashtag_followers
  for delete to authenticated
  using (user_id = auth.uid());

-- RLS for icebreaker_packs
create policy icebreaker_packs_select_all on icebreaker_packs
  for select to authenticated
  using (true);

-- RLS for interaction_tracking
create policy interaction_tracking_select_own on interaction_tracking
  for select to authenticated
  using (user_id = auth.uid());

create policy interaction_tracking_insert_own on interaction_tracking
  for insert to authenticated
  with check (user_id = auth.uid());

create policy interaction_tracking_update_own on interaction_tracking
  for update to authenticated
  using (user_id = auth.uid());

-- Indexes for performance
create index idx_posts_author on posts(author_id);
create index idx_posts_created on posts(created_at desc);
create index idx_comments_post on comments(post_id);
create index idx_comments_author on comments(author_id);
create index idx_post_likes_post on post_likes(post_id);
create index idx_post_likes_liker on post_likes(liker_id);
create index idx_comment_likes_comment on comment_likes(comment_id);
create index idx_post_hashtags_hashtag on post_hashtags(hashtag_id);
create index idx_hashtag_followers_hashtag on hashtag_followers(hashtag_id);
create index idx_interaction_tracking_count on interaction_tracking(total_interactions);

-- Seed initial hashtags/interests
insert into hashtags (name, category, description) values
-- Música
('Drake', 'Música', 'Hip-hop, rap'),
('TaylorSwift', 'Música', 'Pop, country'),
('BadBunny', 'Música', 'Reggaeton, trap latino'),
('Feid', 'Música', 'Reggaeton, trap latino'),
('RauwAlejandro', 'Música', 'Reggaeton, trap latino'),
('TravisScott', 'Música', 'Rap, trap'),
('TheWeeknd', 'Música', 'R&B, pop'),
('Spotify', 'Música', 'Plataforma de música'),
('Rap', 'Música', 'Género rap'),
('Reggaeton', 'Música', 'Género reggaeton'),
('Techno', 'Música', 'Música electrónica'),
('Indie', 'Música', 'Música independiente'),
('Pop', 'Música', 'Música pop'),
('Rock', 'Música', 'Música rock'),
('HipHop', 'Música', 'Hip-hop'),
-- Películas y series
('Netflix', 'Películas y Series', 'Plataforma streaming'),
('Marvel', 'Películas y Series', 'Cine de superhéroes'),
('DC', 'Películas y Series', 'Cine de superhéroes'),
('Series', 'Películas y Series', 'Contenido en series'),
('Películas', 'Películas y Series', 'Cine'),
('Anime', 'Películas y Series', 'Animación japonesa'),
('HBO', 'Películas y Series', 'Plataforma streaming'),
('Disney', 'Películas y Series', 'Entretenimiento familiar'),
-- Redes sociales
('Instagram', 'Redes Sociales', 'Red social de fotos'),
('TikTok', 'Redes Sociales', 'Videos cortos'),
('Snapchat', 'Redes Sociales', 'Mensajería multimedia'),
('YouTube', 'Redes Sociales', 'Plataforma de videos'),
('Twitch', 'Redes Sociales', 'Streaming en vivo'),
-- Deportes
('Futbol', 'Deportes', 'Fútbol'),
('F1', 'Deportes', 'Fórmula 1'),
('NBA', 'Deportes', 'Baloncesto'),
('Gym', 'Deportes', 'Fitness, entrenamiento'),
('Boxeo', 'Deportes', 'Boxeo'),
('Tenis', 'Deportes', 'Tenis'),
('Skateboard', 'Deportes', 'Skateboarding'),
-- Lifestyle
('Viajes', 'Lifestyle', 'Viajes y turismo'),
('Moda', 'Lifestyle', 'Moda y estilo'),
('Coches', 'Lifestyle', 'Automovilismo'),
('Tecnologia', 'Lifestyle', 'Tecnología'),
('Gaming', 'Lifestyle', 'Videojuegos'),
('Fotografia', 'Lifestyle', 'Fotografía'),
('Fiesta', 'Lifestyle', 'Vida nocturna'),
('Conciertos', 'Lifestyle', 'Conciertos y eventos'),
('Universidad', 'Lifestyle', 'Vida universitaria'),
('Lectura', 'Lifestyle', 'Libros'),
('Cafe', 'Lifestyle', 'Café y socialización'),
('Sushi', 'Lifestyle', 'Comida japonesa'),
('Paella', 'Lifestyle', 'Comida española'),
('Pizza', 'Lifestyle', 'Comida italiana'),
('Tacos', 'Lifestyle', 'Comida mexicana'),
-- Salud y bienestar
('Yoga', 'Salud', 'Yoga y meditación'),
('Correr', 'Salud', 'Running'),
('Natacion', 'Salud', 'Natación'),
('Nutricion', 'Salud', 'Nutrición'),
-- Artes
('Dibujo', 'Artes', 'Dibujo y pintura'),
('Musica', 'Artes', 'Tocar instrumentos'),
('Danza', 'Artes', 'Danza y baile'),
('Teatro', 'Artes', 'Arte teatral'),
-- Adicionales
('Naturaleza', 'Outdoor', 'Naturaleza y camping'),
('Montaña', 'Outdoor', 'Montañismo'),
('Playa', 'Outdoor', 'Playas'),
('Senderismo', 'Outdoor', 'Trekking'),
('Gatos', 'Animales', 'Gatos'),
('Perros', 'Animales', 'Perros'),
('Animales', 'Animales', 'Mascotas'),
('Ecologia', 'Valores', 'Sostenibilidad'),
('Feminismo', 'Valores', 'Derechos'),
('Ambiente', 'Valores', 'Medio ambiente'),
('Museos', 'Cultura', 'Arte y museos'),
('Conciencia', 'Valores', 'Desarrollo personal')
on conflict (name) do nothing;

-- Seed icebreaker packs (8 packs with 4-6 phrases each)
insert into icebreaker_packs (pack_number, phrases) values
(1, ARRAY['Hola 👋', 'Ey', '¿Qué tal?', 'Háblame', '¿Hola?', 'Ei, tú']),
(2, ARRAY['Heyy', '¿Qué haces?', '¿Hablamos?', 'Tenemos cosas en común', '¡Hola!', 'Ey, me gustas']),
(3, ARRAY['Me caes bien 👀', '¿De dónde eres?', 'Holaa', 'Ey, tú', '¿Cómo estás?', 'Creo que nos llevamos']),
(4, ARRAY['¿Qué tal todo?', 'Vamos a hablar', 'Pareces interesante', '¿Qué haces?', 'Cuéntame sobre ti', 'Venga a por ti']),
(5, ARRAY['Yo también amo Drake', 'Tenemos gustos parecidos', 'He visto esa serie', '¿Practicas gym?', 'Otro viajero', 'Buenas noches']),
(6, ARRAY['¿Buscas algo casual?', 'Déjame conocerte', 'Anímate a hablar', '¿Nos hablamos?', 'Suena bien', 'Vamos a conocernos']),
(7, ARRAY['¿Cuál es tu historia?', 'Me llamas la atención', '¿Tienes planes?', 'Seguro que tienes cosas interesantes que contar', 'Cuéntame', 'Me atrae tu energía']),
(8, ARRAY['Podemos tener mucho que hablar', 'Empecemos aquí', '¿Que tal charlar?', 'Dime qué te gusta', 'Vamos a vernos bien juntos', 'Creo que encajamos']);

-- Helper functions for likes count management
create or replace function increment_post_likes(post_id uuid)
returns void
language sql
security definer
set search_path = public
as $$
  update posts set likes_count = likes_count + 1 where id = post_id;
$$;

create or replace function decrement_post_likes(post_id uuid)
returns void
language sql
security definer
set search_path = public
as $$
  update posts set likes_count = greatest(likes_count - 1, 0) where id = post_id;
$$;

create or replace function increment_post_comments(post_id uuid)
returns void
language sql
security definer
set search_path = public
as $$
  update posts set comments_count = comments_count + 1 where id = post_id;
$$;

create or replace function increment_comment_likes(comment_id uuid)
returns void
language sql
security definer
set search_path = public
as $$
  update comments set likes_count = likes_count + 1 where id = comment_id;
$$;

create or replace function decrement_comment_likes(comment_id uuid)
returns void
language sql
security definer
set search_path = public
as $$
  update comments set likes_count = greatest(likes_count - 1, 0) where id = comment_id;
$$;

grant execute on function increment_post_likes to authenticated;
grant execute on function decrement_post_likes to authenticated;
grant execute on function increment_post_comments to authenticated;
grant execute on function increment_comment_likes to authenticated;
grant execute on function decrement_comment_likes to authenticated;

-- Grant permissions
grant select on hashtags to authenticated;
grant select on posts to authenticated;
grant insert, update, delete on posts to authenticated;
grant select, insert, delete on post_hashtags to authenticated;
grant select on comments to authenticated;
grant insert, update, delete on comments to authenticated;
grant select, insert, delete on post_likes to authenticated;
grant select, insert, delete on comment_likes to authenticated;
grant select, insert, delete on hashtag_followers to authenticated;
grant select on icebreaker_packs to authenticated;
grant select, insert, update on interaction_tracking to authenticated;
