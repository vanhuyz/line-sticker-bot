from app import db

class Sequence(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  content = db.Column(db.String(1000))
  emoji = db.Column(db.String(1))
  tweet_id = db.Column(db.Integer, db.ForeignKey('tweet.id'))

  def __init__(self, content, emoji, tweet):
    self.content = content
    self.emoji = emoji
    self.tweet_id = tweet.id

  def __repr__(self):
    return '<Sequence id={0}, content={1}, emoji={2}, tweet_id={3}>'.format(self.id, self.content.encode('utf-8'), self.emoji.encode('utf-8'), self.tweet_id)
