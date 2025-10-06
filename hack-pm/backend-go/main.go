package main

import (
	"database/sql"
	"log"
	"net/http"
	"os"
	"strconv"
	"strings"
	"time"

	"github.com/gin-contrib/cors"
	"github.com/gin-gonic/gin"
	_ "github.com/lib/pq"
)

type Project struct {
	ID          int       `json:"id" db:"id"`
	Name        string    `json:"name" db:"name"`
	Description string    `json:"description" db:"description"`
	Status      string    `json:"status" db:"status"`
	CreatedAt   time.Time `json:"created_at" db:"created_at"`
}

type TeamMember struct {
	ID             int       `json:"id" db:"id"`
	ProjectID      int       `json:"project_id" db:"project_id"`
	Name           string    `json:"name" db:"name"`
	Email          string    `json:"email" db:"email"`
	Role           string    `json:"role" db:"role"`
	Skills         []string  `json:"skills"`
	DiscordID      string    `json:"discord_id" db:"discord_id"`
	GithubUsername string    `json:"github_username" db:"github_username"`
	CreatedAt      time.Time `json:"created_at" db:"created_at"`
}

var db *sql.DB

func main() {
	// データベース接続
	var err error
	db, err = sql.Open("postgres", "host=postgres user=hackpm password=hackpm123 dbname=hackpm sslmode=disable")
	if err != nil {
		log.Fatal("データベース接続エラー:", err)
	}
	defer db.Close()

	// テーブル作成
	createTables()

	// Ginルーター設定
	r := gin.Default()

	// CORS設定
	r.Use(cors.New(cors.Config{
		AllowOrigins:     []string{"http://localhost:3000"},
		AllowMethods:     []string{"GET", "POST", "PUT", "DELETE", "OPTIONS"},
		AllowHeaders:     []string{"Origin", "Content-Type", "Accept", "Authorization"},
		ExposeHeaders:    []string{"Content-Length"},
		AllowCredentials: true,
		MaxAge:           12 * time.Hour,
	}))

	// ルート設定
	api := r.Group("/api")
	{
		api.GET("/projects", getProjects)
		api.GET("/projects/:id", getProject)
		api.POST("/projects", createProject)
		api.PUT("/projects/:id", updateProject)
		api.DELETE("/projects/:id", deleteProject)

		// チーム管理
		api.GET("/projects/:id/team", getTeamMembers)
		api.POST("/projects/:id/team", addTeamMember)
		api.DELETE("/projects/:id/team/:member_id", removeTeamMember)

		// 機能管理
		api.GET("/features", getFeatures)
		api.POST("/features", createFeature)
		api.PUT("/features/:id", updateFeature)
		api.DELETE("/features/:id", deleteFeature)
	}

	// ヘルスチェック
	r.Any("/health", func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{"status": "ok"})
	})

	port := os.Getenv("PORT")
	if port == "" {
		port = "8080"
	}

	log.Printf("サーバーをポート %s で起動します", port)
	r.Run(":" + port)
}

func createTables() {
	// プロジェクトテーブル
	projectQuery := `
	CREATE TABLE IF NOT EXISTS projects (
		id SERIAL PRIMARY KEY,
		name VARCHAR(255) NOT NULL,
		description TEXT,
		status VARCHAR(50) DEFAULT 'active',
		created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
	);`

	_, err := db.Exec(projectQuery)
	if err != nil {
		log.Fatal("プロジェクトテーブル作成エラー:", err)
	}

	// チームメンバーテーブル
	memberQuery := `
	CREATE TABLE IF NOT EXISTS team_members (
		id SERIAL PRIMARY KEY,
		project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
		name VARCHAR(255) NOT NULL,
		email VARCHAR(255) NOT NULL,
		role VARCHAR(100) DEFAULT 'developer',
		skills TEXT,
		discord_id VARCHAR(255),
		github_username VARCHAR(255),
		created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
	);`

	_, err = db.Exec(memberQuery)
	if err != nil {
		log.Fatal("チームメンバーテーブル作成エラー:", err)
	}

	// 機能テーブル
	featureQuery := `
	CREATE TABLE IF NOT EXISTS features (
		id SERIAL PRIMARY KEY,
		title VARCHAR(255) NOT NULL,
		description TEXT,
		status VARCHAR(50) DEFAULT 'todo',
		priority VARCHAR(50) DEFAULT 'medium',
		assignee VARCHAR(255),
		estimated_hours INTEGER DEFAULT 0,
		actual_hours INTEGER,
		start_date DATE,
		end_date DATE,
		tags TEXT,
		created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
	);`

	_, err = db.Exec(featureQuery)
	if err != nil {
		log.Fatal("機能テーブル作成エラー:", err)
	}

	// サンプルデータ挿入
	insertSampleData()
}

func insertSampleData() {
	var count int
	err := db.QueryRow("SELECT COUNT(*) FROM projects").Scan(&count)
	if err != nil || count > 0 {
		return
	}

	sampleProjects := []Project{
		{Name: "AIチャットボット", Description: "自然言語処理を使ったチャットボットの開発", Status: "active"},
		{Name: "IoTセンサーダッシュボード", Description: "センサーデータの可視化システム", Status: "active"},
		{Name: "ブロックチェーン投票システム", Description: "透明性の高い投票システムの構築", Status: "completed"},
	}

	for _, project := range sampleProjects {
		_, err := db.Exec(
			"INSERT INTO projects (name, description, status) VALUES ($1, $2, $3)",
			project.Name, project.Description, project.Status,
		)
		if err != nil {
			log.Printf("サンプルデータ挿入エラー: %v", err)
		}
	}
}

func getProjects(c *gin.Context) {
	rows, err := db.Query("SELECT id, name, description, status, created_at FROM projects ORDER BY created_at DESC")
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}
	defer rows.Close()

	var projects []Project
	for rows.Next() {
		var project Project
		err := rows.Scan(&project.ID, &project.Name, &project.Description, &project.Status, &project.CreatedAt)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
			return
		}
		projects = append(projects, project)
	}

	c.JSON(http.StatusOK, projects)
}

func getProject(c *gin.Context) {
	id, err := strconv.Atoi(c.Param("id"))
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "無効なID"})
		return
	}

	var project Project
	err = db.QueryRow(
		"SELECT id, name, description, status, created_at FROM projects WHERE id = $1",
		id,
	).Scan(&project.ID, &project.Name, &project.Description, &project.Status, &project.CreatedAt)

	if err != nil {
		if err == sql.ErrNoRows {
			c.JSON(http.StatusNotFound, gin.H{"error": "プロジェクトが見つかりません"})
		} else {
			c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		}
		return
	}

	c.JSON(http.StatusOK, project)
}

func createProject(c *gin.Context) {
	var project Project
	if err := c.ShouldBindJSON(&project); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	err := db.QueryRow(
		"INSERT INTO projects (name, description, status) VALUES ($1, $2, $3) RETURNING id, created_at",
		project.Name, project.Description, project.Status,
	).Scan(&project.ID, &project.CreatedAt)

	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusCreated, project)
}

func updateProject(c *gin.Context) {
	id, err := strconv.Atoi(c.Param("id"))
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "無効なID"})
		return
	}

	var project Project
	if err := c.ShouldBindJSON(&project); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	_, err = db.Exec(
		"UPDATE projects SET name = $1, description = $2, status = $3 WHERE id = $4",
		project.Name, project.Description, project.Status, id,
	)

	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	project.ID = id
	c.JSON(http.StatusOK, project)
}

func deleteProject(c *gin.Context) {
	id, err := strconv.Atoi(c.Param("id"))
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "無効なID"})
		return
	}

	_, err = db.Exec("DELETE FROM projects WHERE id = $1", id)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, gin.H{"message": "プロジェクトが削除されました"})
}

func getTeamMembers(c *gin.Context) {
	projectID, err := strconv.Atoi(c.Param("id"))
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "無効なプロジェクトID"})
		return
	}

	rows, err := db.Query(`
		SELECT id, project_id, name, email, role, COALESCE(skills, ''), 
		       COALESCE(discord_id, ''), COALESCE(github_username, ''), created_at 
		FROM team_members WHERE project_id = $1 ORDER BY created_at DESC
	`, projectID)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}
	defer rows.Close()

	var members []TeamMember
	for rows.Next() {
		var member TeamMember
		var skillsStr string
		err := rows.Scan(&member.ID, &member.ProjectID, &member.Name, &member.Email,
			&member.Role, &skillsStr, &member.DiscordID, &member.GithubUsername, &member.CreatedAt)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
			return
		}

		// スキルを配列に変換
		if skillsStr != "" {
			member.Skills = strings.Split(skillsStr, ",")
			for i, skill := range member.Skills {
				member.Skills[i] = strings.TrimSpace(skill)
			}
		}

		members = append(members, member)
	}

	c.JSON(http.StatusOK, members)
}

func addTeamMember(c *gin.Context) {
	projectID, err := strconv.Atoi(c.Param("id"))
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "無効なプロジェクトID"})
		return
	}

	var member TeamMember
	if err := c.ShouldBindJSON(&member); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	member.ProjectID = projectID
	skillsStr := strings.Join(member.Skills, ",")

	err = db.QueryRow(`
		INSERT INTO team_members (project_id, name, email, role, skills, discord_id, github_username) 
		VALUES ($1, $2, $3, $4, $5, $6, $7) RETURNING id, created_at
	`, member.ProjectID, member.Name, member.Email, member.Role, skillsStr,
		member.DiscordID, member.GithubUsername).Scan(&member.ID, &member.CreatedAt)

	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusCreated, member)
}

func removeTeamMember(c *gin.Context) {
	projectID, err := strconv.Atoi(c.Param("id"))
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "無効なプロジェクトID"})
		return
	}

	memberID, err := strconv.Atoi(c.Param("member_id"))
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "無効なメンバーID"})
		return
	}

	_, err = db.Exec("DELETE FROM team_members WHERE id = $1 AND project_id = $2", memberID, projectID)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, gin.H{"message": "チームメンバーが削除されました"})
}

type Feature struct {
	ID             int       `json:"id" db:"id"`
	Title          string    `json:"title" db:"title"`
	Description    string    `json:"description" db:"description"`
	Status         string    `json:"status" db:"status"`
	Priority       string    `json:"priority" db:"priority"`
	Assignee       string    `json:"assignee" db:"assignee"`
	EstimatedHours int       `json:"estimatedHours" db:"estimated_hours"`
	ActualHours    *int      `json:"actualHours" db:"actual_hours"`
	StartDate      string    `json:"startDate" db:"start_date"`
	EndDate        string    `json:"endDate" db:"end_date"`
	Tags           []string  `json:"tags"`
	CreatedAt      time.Time `json:"created_at" db:"created_at"`
}

func getFeatures(c *gin.Context) {
	rows, err := db.Query(`
		SELECT id, title, description, status, priority, assignee, 
		       estimated_hours, actual_hours, start_date, end_date, 
		       COALESCE(tags, ''), created_at 
		FROM features ORDER BY created_at DESC
	`)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}
	defer rows.Close()

	var features []Feature
	for rows.Next() {
		var feature Feature
		var tagsStr string
		err := rows.Scan(&feature.ID, &feature.Title, &feature.Description,
			&feature.Status, &feature.Priority, &feature.Assignee,
			&feature.EstimatedHours, &feature.ActualHours, &feature.StartDate,
			&feature.EndDate, &tagsStr, &feature.CreatedAt)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
			return
		}

		if tagsStr != "" {
			feature.Tags = strings.Split(tagsStr, ",")
			for i, tag := range feature.Tags {
				feature.Tags[i] = strings.TrimSpace(tag)
			}
		}

		features = append(features, feature)
	}

	c.JSON(http.StatusOK, features)
}

func createFeature(c *gin.Context) {
	var feature Feature
	if err := c.ShouldBindJSON(&feature); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	tagsStr := strings.Join(feature.Tags, ",")

	err := db.QueryRow(`
		INSERT INTO features (title, description, status, priority, assignee, 
		                     estimated_hours, start_date, end_date, tags) 
		VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9) RETURNING id, created_at
	`, feature.Title, feature.Description, feature.Status, feature.Priority,
		feature.Assignee, feature.EstimatedHours, feature.StartDate,
		feature.EndDate, tagsStr).Scan(&feature.ID, &feature.CreatedAt)

	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusCreated, feature)
}

func updateFeature(c *gin.Context) {
	id, err := strconv.Atoi(c.Param("id"))
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "無効なID"})
		return
	}

	var feature Feature
	if err := c.ShouldBindJSON(&feature); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	tagsStr := strings.Join(feature.Tags, ",")

	_, err = db.Exec(`
		UPDATE features SET title = $1, description = $2, status = $3, 
		                   priority = $4, assignee = $5, estimated_hours = $6,
		                   actual_hours = $7, start_date = $8, end_date = $9, tags = $10
		WHERE id = $11
	`, feature.Title, feature.Description, feature.Status, feature.Priority,
		feature.Assignee, feature.EstimatedHours, feature.ActualHours,
		feature.StartDate, feature.EndDate, tagsStr, id)

	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	feature.ID = id
	c.JSON(http.StatusOK, feature)
}

func deleteFeature(c *gin.Context) {
	id, err := strconv.Atoi(c.Param("id"))
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "無効なID"})
		return
	}

	_, err = db.Exec("DELETE FROM features WHERE id = $1", id)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, gin.H{"message": "機能が削除されました"})
}
