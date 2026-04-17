-- Seed data: 20 manually labeled profiles to bootstrap model training.
-- Real accounts have high engagement, good bio, natural posting patterns.
-- Fake accounts have low engagement, bad ratios, empty bios.
-- Expand this to 200+ profiles before training seriously.

INSERT INTO profiles (username, follower_count, following_count, post_count, is_verified, bio)
VALUES
  ('seed_real_01', 12400, 890, 234, false, 'Travel photographer based in Berlin'),
  ('seed_real_02', 8900, 420, 178, false, 'Food blogger | Hamburg | collabs: dm me'),
  ('seed_real_03', 45000, 1200, 512, true, 'Official account - lifestyle brand'),
  ('seed_real_04', 3200, 310, 89, false, 'Amateur cyclist | coffee addict'),
  ('seed_real_05', 22000, 980, 301, false, 'Fitness coach | online programs available'),
  ('seed_fake_01', 94000, 87000, 12, false, ''),
  ('seed_fake_02', 150000, 145000, 8, false, 'Hi'),
  ('seed_fake_03', 78000, 72000, 45, false, ''),
  ('seed_fake_04', 210000, 198000, 23, false, 'follow back'),
  ('seed_fake_05', 55000, 51000, 6, false, '');

INSERT INTO fake_signals (
  profile_id, label,
  engagement_rate, follower_following_ratio, avg_likes_per_post,
  avg_comments_per_post, comment_like_ratio, posting_consistency_cv,
  ghost_follower_estimate, bio_completeness_score
)
SELECT p.id,
  CASE WHEN p.username LIKE 'seed_real%' THEN 'real' ELSE 'fake' END,
  CASE WHEN p.username LIKE 'seed_real%' THEN (random()*4+1) ELSE (random()*0.4) END,
  CASE WHEN p.username LIKE 'seed_real%' THEN (p.follower_count::float / NULLIF(p.following_count,0)) ELSE (random()*0.2+0.9) END,
  CASE WHEN p.username LIKE 'seed_real%' THEN (p.follower_count * (random()*0.04+0.01)) ELSE (p.follower_count * random()*0.003) END,
  CASE WHEN p.username LIKE 'seed_real%' THEN (p.follower_count * (random()*0.002+0.0005)) ELSE (p.follower_count * random()*0.0001) END,
  CASE WHEN p.username LIKE 'seed_real%' THEN (random()*0.08+0.02) ELSE (random()*0.005) END,
  CASE WHEN p.username LIKE 'seed_real%' THEN (random()*0.8+0.3) ELSE (random()*0.1) END,
  CASE WHEN p.username LIKE 'seed_real%' THEN (random()*0.25) ELSE (random()*0.4+0.55) END,
  CASE WHEN p.username LIKE 'seed_real%' THEN (random()*0.5+0.4) ELSE (random()*0.15) END
FROM profiles p
WHERE p.username LIKE 'seed_%';
