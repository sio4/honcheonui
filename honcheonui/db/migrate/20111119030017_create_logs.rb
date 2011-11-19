class CreateLogs < ActiveRecord::Migration
  def change
    create_table :logs do |t|
      t.datetime :logdate
      t.references :server
      t.string :process
      t.integer :pid
      t.string :message

      t.timestamps
    end
    add_index :logs, :server_id
  end
end
