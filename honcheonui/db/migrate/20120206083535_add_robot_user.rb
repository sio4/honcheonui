class AddRobotUser < ActiveRecord::Migration
  def up
    User.create! (
      :email => 'agent@example.com',
      :password => 'fLzewhqjQEHh7ShPrZpn',
      :name => 'rRobot',
      :mail => 'agent@example.com',
      :level => 0,
      :active => true
    )
  end

  def down
    User.where(:email => 'agent@example.com').first.delete
  end
end
