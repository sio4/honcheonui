class CreateStats < ActiveRecord::Migration
  def change
    create_table :stats do |t|
      t.references :server
      t.datetime :dt
      t.integer :cpu_user_max
      t.integer :cpu_user_avg
      t.integer :cpu_sys_max
      t.integer :cpu_sys_avg
      t.integer :cpu_wait_max
      t.integer :cpu_wait_avg
      t.integer :mem_used
      t.integer :mem_buffer
      t.integer :mem_cached
      t.integer :swp_used
      t.integer :task_total
      t.integer :task_running
      t.integer :task_blocked
      t.integer :task_zombie
      t.integer :users

      t.timestamps
    end
    add_index :stats, :server_id
  end
end
