<?php
// index.php - Adminer Favorites
$favorites = [
    'Ingest DB - Local Container (Main Server)' => [
        'server' => 'ingest-database',
        'username' => 'ingestuser',
        'db' => 'ingest_db',
    ],
    'Device DB - Device Manager' => [
        'server' => 'device-database',
        'username' => 'iot',
        'db' => 'device_db',
    ],
    'Analytics DB' => [
        'server' => 'analytics-database',
        'username' => 'analytics_user',
        'db' => 'analytics_db',
    ],
    'Ingest DB - Pi3-fr-dnr (LAN)' => [
        'server' => '10.44.1.223',
        'username' => 'ingestuser',
        'db' => 'ingest_db',
    ],
];
?>
<!DOCTYPE html>
<html>
<head>
  <title>Adminer Favorites</title>
  <style>
    body { font-family: sans-serif; margin: 2em; }
    h1 { color: #333; }
    ul { list-style-type: none; padding: 0; }
    li { margin-bottom: 1em; }
    a { text-decoration: none; font-weight: bold; color: #0055cc; }
    a:hover { text-decoration: underline; }
    .desc { font-size: 0.9em; color: #666; }
  </style>
</head>
<body>
  <h1>📚 Adminer Database Shortcuts</h1>
  <ul>
    <?php foreach ($favorites as $label => $data): ?>
      <li>
        <a href="adminer.php?server=<?= urlencode($data['server']) ?>&username=<?= urlencode($data['username']) ?>&db=<?= urlencode($data['db']) ?>">
          <?= htmlspecialchars($label) ?>
        </a><br>
        <span class="desc"><?= htmlspecialchars($data['server']) ?> &middot; <?= htmlspecialchars($data['username']) ?> &middot; <?= htmlspecialchars($data['db']) ?></span>
      </li>
    <?php endforeach; ?>
  </ul>
</body>
</html>
