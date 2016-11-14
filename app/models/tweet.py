from app import db

class Tweet(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  content = db.Column(db.String(1000))

  def __init__(self, content):
    self.content = content

  def __repr__(self):
    return '<Tweet id={0}, content={1}>'.format(self.id, self.content.encode('utf-8'))
