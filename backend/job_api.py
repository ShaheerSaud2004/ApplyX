#!/usr/bin/env python3

from flask import Blueprint, jsonify, request
from typing import Dict, List, Any
import sqlite3
import json
import datetime
import asyncio

job_bp = Blueprint('jobs', __name__)

def register_job_routes(app):
    """Register job-related routes with the Flask app"""
    app.register_blueprint(job_bp)

@job_bp.route('/api/jobs', methods=['GET'])
def get_jobs():
    try:
        category = request.args.get('category', 'all')
        search = request.args.get('search', '')
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 20))
        sort_by = request.args.get('sort_by', 'posted_date')
        sort_order = request.args.get('sort_order', 'DESC')
        experience_level = request.args.get('experience_level', 'all')
        is_remote = request.args.get('is_remote', 'all')
        
        offset = (page - 1) * limit
        
        conn = sqlite3.connect('job_listings.db')
        cursor = conn.cursor()
        
        query = "SELECT * FROM job_listings WHERE 1=1"
        params = []
        
        if category and category != 'all':
            query += " AND category = ?"
            params.append(category)
            
        if search:
            query += " AND (title LIKE ? OR company LIKE ? OR description LIKE ?)"
            search_param = f"%{search}%"
            params.extend([search_param, search_param, search_param])
            
        if experience_level != 'all':
            query += " AND experience_level = ?"
            params.append(experience_level)
            
        if is_remote != 'all':
            is_remote_bool = 1 if is_remote.lower() == 'true' else 0
            query += " AND is_remote = ?"
            params.append(is_remote_bool)
        
        query += f" ORDER BY {sort_by} {sort_order} LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        jobs = [dict(zip(columns, row)) for row in rows]
        
        # Parse tags JSON
        for job in jobs:
            if job.get('tags'):
                try:
                    job['tags'] = json.loads(job['tags'])
                except:
                    job['tags'] = []
            else:
                job['tags'] = []
        
        conn.close()
        
        return jsonify({
            'jobs': jobs,
            'page': page,
            'limit': limit,
            'total': len(jobs),
            'has_more': len(jobs) == limit
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@job_bp.route('/api/jobs/categories', methods=['GET'])
def get_job_categories():
    try:
        conn = sqlite3.connect('job_listings.db')
        cursor = conn.cursor()
        cursor.execute('''
            SELECT category, COUNT(*) as count 
            FROM job_listings 
            GROUP BY category 
            ORDER BY count DESC
        ''')
        results = cursor.fetchall()
        category_counts = {category: count for category, count in results}
        
        # Get total jobs
        cursor.execute('SELECT COUNT(*) FROM job_listings')
        total_jobs = cursor.fetchone()[0]
        
        conn.close()
        
        enhanced_categories = {
            'software': {'label': 'Software Development', 'icon': 'Code', 'color': 'bg-purple-100 text-purple-800 border-purple-200', 'description': 'Frontend, backend, full-stack, and mobile development roles', 'count': category_counts.get('software', 0)},
            'data': {'label': 'Data Science & Analytics', 'icon': 'BarChart3', 'color': 'bg-indigo-100 text-indigo-800 border-indigo-200', 'description': 'Data science, machine learning, and analytics positions', 'count': category_counts.get('data', 0)},
            'cybersecurity': {'label': 'Cybersecurity', 'icon': 'Shield', 'color': 'bg-red-100 text-red-800 border-red-200', 'description': 'Information security and cybersecurity roles', 'count': category_counts.get('cybersecurity', 0)},
            'it': {'label': 'IT & Infrastructure', 'icon': 'Server', 'color': 'bg-green-100 text-green-800 border-green-200', 'description': 'DevOps, system administration, and cloud infrastructure', 'count': category_counts.get('it', 0)},
            'product': {'label': 'Product Management', 'icon': 'Lightbulb', 'color': 'bg-yellow-100 text-yellow-800 border-yellow-200', 'description': 'Product management and strategy roles', 'count': category_counts.get('product', 0)},
            'design': {'label': 'Design & UX', 'icon': 'Palette', 'color': 'bg-pink-100 text-pink-800 border-pink-200', 'description': 'UI/UX design and creative positions', 'count': category_counts.get('design', 0)},
            'marketing': {'label': 'Marketing & Growth', 'icon': 'TrendingUp', 'color': 'bg-orange-100 text-orange-800 border-orange-200', 'description': 'Digital marketing, growth, and content roles', 'count': category_counts.get('marketing', 0)},
            'sales': {'label': 'Sales & Business Dev', 'icon': 'Users', 'color': 'bg-blue-100 text-blue-800 border-blue-200', 'description': 'Sales, business development, and customer success', 'count': category_counts.get('sales', 0)},
            'finance': {'label': 'Finance & Accounting', 'icon': 'DollarSign', 'color': 'bg-emerald-100 text-emerald-800 border-emerald-200', 'description': 'Financial analysis, accounting, and treasury roles', 'count': category_counts.get('finance', 0)},
            'hr': {'label': 'Human Resources', 'icon': 'Heart', 'color': 'bg-rose-100 text-rose-800 border-rose-200', 'description': 'HR, recruiting, and people operations', 'count': category_counts.get('hr', 0)},
            'operations': {'label': 'Operations', 'icon': 'Settings', 'color': 'bg-gray-100 text-gray-800 border-gray-200', 'description': 'Operations, logistics, and supply chain management', 'count': category_counts.get('operations', 0)},
            'legal': {'label': 'Legal & Compliance', 'icon': 'Scale', 'color': 'bg-slate-100 text-slate-800 border-slate-200', 'description': 'Legal counsel, compliance, and regulatory roles', 'count': category_counts.get('legal', 0)},
            'healthcare': {'label': 'Healthcare', 'icon': 'Cross', 'color': 'bg-cyan-100 text-cyan-800 border-cyan-200', 'description': 'Medical, clinical, and healthcare positions', 'count': category_counts.get('healthcare', 0)},
            'education': {'label': 'Education & Research', 'icon': 'GraduationCap', 'color': 'bg-violet-100 text-violet-800 border-violet-200', 'description': 'Academic, research, and educational roles', 'count': category_counts.get('education', 0)},
            'consulting': {'label': 'Consulting', 'icon': 'MessageSquare', 'color': 'bg-teal-100 text-teal-800 border-teal-200', 'description': 'Management consulting and advisory positions', 'count': category_counts.get('consulting', 0)},
            'engineering': {'label': 'Engineering', 'icon': 'Cog', 'color': 'bg-amber-100 text-amber-800 border-amber-200', 'description': 'Mechanical, electrical, and other engineering roles', 'count': category_counts.get('engineering', 0)},
            'startup': {'label': 'Startup & Entrepreneurship', 'icon': 'Rocket', 'color': 'bg-lime-100 text-lime-800 border-lime-200', 'description': 'Startup roles and entrepreneurial opportunities', 'count': category_counts.get('startup', 0)},
            'other': {'label': 'Other', 'icon': 'MoreHorizontal', 'color': 'bg-neutral-100 text-neutral-800 border-neutral-200', 'description': 'Miscellaneous and uncategorized positions', 'count': category_counts.get('other', 0)},
        }
        
        return jsonify({
            'categories': enhanced_categories,
            'total_jobs': total_jobs
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@job_bp.route('/api/jobs/stats', methods=['GET'])
def get_job_stats():
    try:
        conn = sqlite3.connect('job_listings.db')
        cursor = conn.cursor()
        
        # Total jobs
        cursor.execute('SELECT COUNT(*) FROM job_listings')
        total_jobs = cursor.fetchone()[0]
        
        # Jobs added today
        cursor.execute('''
            SELECT COUNT(*) FROM job_listings 
            WHERE DATE(created_at) = DATE('now')
        ''')
        jobs_today = cursor.fetchone()[0]
        
        # Jobs added this week
        cursor.execute('''
            SELECT COUNT(*) FROM job_listings 
            WHERE DATE(created_at) >= DATE('now', '-7 days')
        ''')
        jobs_this_week = cursor.fetchone()[0]
        
        # Remote jobs
        cursor.execute('SELECT COUNT(*) FROM job_listings WHERE is_remote = 1')
        remote_jobs = cursor.fetchone()[0]
        
        conn.close()
        
        return jsonify({
            'total_jobs': total_jobs,
            'jobs_today': jobs_today,
            'jobs_this_week': jobs_this_week,
            'remote_jobs': remote_jobs,
            'remote_percentage': round((remote_jobs / total_jobs * 100) if total_jobs > 0 else 0, 1)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@job_bp.route('/api/jobs/trending', methods=['GET'])
def get_trending_jobs():
    try:
        conn = sqlite3.connect('job_listings.db')
        cursor = conn.cursor()
        
        # Trending job titles (most common)
        cursor.execute('''
            SELECT title, COUNT(*) as count 
            FROM job_listings 
            GROUP BY LOWER(title) 
            ORDER BY count DESC 
            LIMIT 10
        ''')
        trending_titles = [{'title': title, 'count': count} for title, count in cursor.fetchall()]
        
        # Trending companies
        cursor.execute('''
            SELECT company, COUNT(*) as count 
            FROM job_listings 
            GROUP BY LOWER(company) 
            ORDER BY count DESC 
            LIMIT 10
        ''')
        trending_companies = [{'company': company, 'count': count} for company, count in cursor.fetchall()]
        
        # Trending locations
        cursor.execute('''
            SELECT location, COUNT(*) as count 
            FROM job_listings 
            WHERE location != '' AND location IS NOT NULL
            GROUP BY LOWER(location) 
            ORDER BY count DESC 
            LIMIT 10
        ''')
        trending_locations = [{'location': location, 'count': count} for location, count in cursor.fetchall()]
        
        conn.close()
        
        return jsonify({
            'trending_titles': trending_titles,
            'trending_companies': trending_companies,
            'trending_locations': trending_locations
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@job_bp.route('/api/jobs/update', methods=['POST'])
def update_jobs():
    """Manual endpoint to trigger job updates"""
    try:
        from job_aggregator import JobAggregator
        
        aggregator = JobAggregator()
        
        # Run the update in an async context
        def run_update():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(aggregator.update_all_jobs())
            loop.close()
            return result
        
        result = run_update()
        
        return jsonify({
            'success': True,
            'message': f'Successfully updated {result} jobs!',
            'jobs_updated': result
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@job_bp.route('/api/jobs/<job_id>', methods=['PUT'])
def update_job(job_id):
    """Update a specific job's details"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        # Validate job_id
        if not job_id:
            return jsonify({'error': 'Job ID is required'}), 400
            
        conn = sqlite3.connect('job_listings.db')
        cursor = conn.cursor()
        
        # Check if job exists
        cursor.execute('SELECT id FROM job_listings WHERE id = ?', (job_id,))
        if not cursor.fetchone():
            conn.close()
            return jsonify({'error': 'Job not found'}), 404
        
        # Build update query dynamically based on provided fields
        update_fields = []
        update_values = []
        
        if 'category' in data:
            update_fields.append('category = ?')
            update_values.append(data['category'])
            
        if 'title' in data:
            update_fields.append('title = ?')
            update_values.append(data['title'])
            
        if 'company' in data:
            update_fields.append('company = ?')
            update_values.append(data['company'])
            
        if 'location' in data:
            update_fields.append('location = ?')
            update_values.append(data['location'])
            
        if 'experience_level' in data:
            update_fields.append('experience_level = ?')
            update_values.append(data['experience_level'])
            
        if 'is_remote' in data:
            update_fields.append('is_remote = ?')
            update_values.append(int(data['is_remote']))
        
        if not update_fields:
            conn.close()
            return jsonify({'error': 'No valid fields to update'}), 400
        
        # Add updated timestamp
        update_fields.append('updated_at = ?')
        update_values.append(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        
        # Add job_id for WHERE clause
        update_values.append(job_id)
        
        # Execute update
        update_query = f"UPDATE job_listings SET {', '.join(update_fields)} WHERE id = ?"
        cursor.execute(update_query, update_values)
        
        if cursor.rowcount == 0:
            conn.close()
            return jsonify({'error': 'No changes made'}), 400
            
        conn.commit()
        
        # Fetch updated job
        cursor.execute('''
            SELECT id, title, company, location, url, category, 
                   experience_level, is_remote, salary, description,
                   tags, posted_date, created_at, updated_at, source
            FROM job_listings WHERE id = ?
        ''', (job_id,))
        
        job = cursor.fetchone()
        conn.close()
        
        if job:
            job_dict = {
                'id': job[0],
                'title': job[1],
                'company': job[2],
                'location': job[3],
                'url': job[4],
                'category': job[5],
                'experience_level': job[6],
                'is_remote': bool(job[7]),
                'salary': job[8],
                'description': job[9],
                'tags': json.loads(job[10]) if job[10] else [],
                'posted_date': job[11],
                'created_at': job[12],
                'updated_at': job[13],
                'source': job[14]
            }
            
            return jsonify({
                'success': True,
                'message': 'Job updated successfully',
                'job': job_dict
            })
        else:
            return jsonify({'error': 'Failed to fetch updated job'}), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500 