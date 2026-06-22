package models

import "time"

type Base struct {
	Id          uint      `gorm:"primaryKey"`
	CreatedDate time.Time `gorm:"column:created_at"`
	UpdatedDate time.Time `gorm:"column:updated_at"`
	DeletedDate time.Time `gorm:"column:deleted_at;index"`
}
