"""
Complete System Startup and Verification Script
Starts backend, frontend, and runs comprehensive checks
"""
import subprocess
import time
import requests
import sys
from pathlib import Path
import os


class SystemStarter:
    """Start and verify all system components"""
    
    def __init__(self):
        self.backend_url = "http://localhost:8000"
        self.frontend_url = "http://localhost:5173"
        self.processes = []
    
    def check_prerequisites(self):
        """Check if required tools are installed"""
        print("="*80)
        print("🔍 CHECKING PREREQUISITES")
        print("="*80)
        
        checks = {
            "Python": ["python", "--version"],
            "Node.js": ["node", "--version"],
            "npm": ["npm", "--version"],
        }
        
        all_good = True
        for name, cmd in checks.items():
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
                version = result.stdout.strip() or result.stderr.strip()
                print(f"✅ {name}: {version}")
            except Exception as e:
                print(f"❌ {name}: Not found")
                all_good = False
        
        return all_good
    
    def check_optional_services(self):
        """Check optional services (Redis, PostgreSQL, Celery)"""
        print("\n" + "="*80)
        print("🔍 CHECKING OPTIONAL SERVICES")
        print("="*80)
        
        # Check Redis
        try:
            result = subprocess.run(
                ["redis-cli", "ping"],
                capture_output=True,
                text=True,
                timeout=2
            )
            if "PONG" in result.stdout:
                print("✅ Redis: Running")
            else:
                print("⚠️  Redis: Not running (optional - caching disabled)")
        except:
            print("⚠️  Redis: Not running (optional - caching disabled)")
        
        # Check PostgreSQL
        try:
            result = subprocess.run(
                ["pg_isready", "-h", "localhost", "-p", "5432"],
                capture_output=True,
                text=True,
                timeout=2
            )
            if "accepting connections" in result.stdout:
                print("✅ PostgreSQL: Running")
            else:
                print("⚠️  PostgreSQL: Not running (optional - using JSON storage)")
        except:
            print("⚠️  PostgreSQL: Not running (optional - using JSON storage)")
        
        print("\nNote: Redis and PostgreSQL are optional.")
        print("      System works without them (just slower/no persistence)")
    
    def start_backend(self):
        """Start FastAPI backend"""
        print("\n" + "="*80)
        print("🚀 STARTING BACKEND")
        print("="*80)
        
        backend_dir = Path("backend")
        if not backend_dir.exists():
            print("❌ Backend directory not found")
            return False
        
        print("Starting FastAPI backend on http://localhost:8000...")
        
        try:
            # Start backend process
            process = subprocess.Popen(
                ["uvicorn", "app.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"],
                cwd=backend_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            self.processes.append(("Backend", process))
            
            # Wait for backend to start
            print("Waiting for backend to start...")
            max_wait = 30
            for i in range(max_wait):
                try:
                    response = requests.get(f"{self.backend_url}/health", timeout=1)
                    if response.status_code == 200:
                        print(f"✅ Backend started successfully in {i+1}s")
                        return True
                except:
                    time.sleep(1)
                    if i % 5 == 0:
                        print(f"   Still waiting... ({i+1}s)")
            
            print("❌ Backend failed to start within 30s")
            return False
            
        except Exception as e:
            print(f"❌ Failed to start backend: {e}")
            return False
    
    def start_frontend(self):
        """Start React frontend"""
        print("\n" + "="*80)
        print("🚀 STARTING FRONTEND")
        print("="*80)
        
        frontend_dir = Path("marketshield-frontend")
        if not frontend_dir.exists():
            print("❌ Frontend directory not found")
            return False
        
        # Check if node_modules exists
        if not (frontend_dir / "node_modules").exists():
            print("📦 Installing frontend dependencies...")
            try:
                subprocess.run(
                    ["npm", "install"],
                    cwd=frontend_dir,
                    check=True
                )
                print("✅ Dependencies installed")
            except Exception as e:
                print(f"❌ Failed to install dependencies: {e}")
                return False
        
        print("Starting React frontend on http://localhost:5173...")
        
        try:
            # Start frontend process
            process = subprocess.Popen(
                ["npm", "run", "dev"],
                cwd=frontend_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            self.processes.append(("Frontend", process))
            
            # Wait for frontend to start
            print("Waiting for frontend to start...")
            max_wait = 60
            for i in range(max_wait):
                try:
                    response = requests.get(self.frontend_url, timeout=1)
                    if response.status_code == 200:
                        print(f"✅ Frontend started successfully in {i+1}s")
                        return True
                except:
                    time.sleep(1)
                    if i % 10 == 0:
                        print(f"   Still waiting... ({i+1}s)")
            
            print("❌ Frontend failed to start within 60s")
            return False
            
        except Exception as e:
            print(f"❌ Failed to start frontend: {e}")
            return False
    
    def verify_backend(self):
        """Verify backend is working"""
        print("\n" + "="*80)
        print("✅ VERIFYING BACKEND")
        print("="*80)
        
        try:
            # Health check
            response = requests.get(f"{self.backend_url}/api/v1/intelligence/health")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Health check passed")
                print(f"   Service: {data['service']}")
                print(f"   Version: {data['version']}")
                
                # Check features
                print("\n📊 Features:")
                features = data.get('features', {})
                for feature, enabled in features.items():
                    status = "✅" if enabled else "❌"
                    print(f"   {status} {feature}: {enabled}")
                
                # Check cache
                cache = data.get('cache', {})
                if cache.get('enabled'):
                    print(f"\n💾 Cache: Enabled")
                    print(f"   Hit rate: {cache.get('hit_rate', 0)}%")
                else:
                    print(f"\n⚠️  Cache: Disabled (Redis not running)")
                
                # Check database
                db = data.get('database', {})
                if db.get('enabled'):
                    print(f"\n💾 Database: Enabled")
                    print(f"   Dual-write: {db.get('dual_write')}")
                else:
                    print(f"\n⚠️  Database: Disabled (PostgreSQL not running)")
                
                # Check Celery
                celery = data.get('celery', {})
                if celery.get('enabled'):
                    print(f"\n🔄 Celery: Enabled")
                    print(f"   Async endpoints: Available")
                else:
                    print(f"\n⚠️  Celery: Disabled (Celery worker not running)")
                
                return True
            else:
                print(f"❌ Health check failed: {response.status_code}")
                return False
        
        except Exception as e:
            print(f"❌ Backend verification failed: {e}")
            return False
    
    def verify_frontend(self):
        """Verify frontend is working"""
        print("\n" + "="*80)
        print("✅ VERIFYING FRONTEND")
        print("="*80)
        
        try:
            response = requests.get(self.frontend_url, timeout=5)
            if response.status_code == 200:
                print(f"✅ Frontend is accessible")
                print(f"   URL: {self.frontend_url}")
                return True
            else:
                print(f"❌ Frontend returned: {response.status_code}")
                return False
        
        except Exception as e:
            print(f"❌ Frontend verification failed: {e}")
            return False
    
    def test_api_endpoint(self):
        """Test a simple API endpoint"""
        print("\n" + "="*80)
        print("🧪 TESTING API ENDPOINT")
        print("="*80)
        
        try:
            print("Testing intelligence health endpoint...")
            response = requests.get(
                f"{self.backend_url}/api/v1/intelligence/health",
                timeout=5
            )
            
            if response.status_code == 200:
                print("✅ API endpoint working")
                return True
            else:
                print(f"❌ API endpoint failed: {response.status_code}")
                return False
        
        except Exception as e:
            print(f"❌ API test failed: {e}")
            return False
    
    def print_summary(self):
        """Print startup summary"""
        print("\n" + "="*80)
        print("📋 STARTUP SUMMARY")
        print("="*80)
        
        print("\n✅ RUNNING SERVICES:")
        print(f"   • Backend:  {self.backend_url}")
        print(f"   • Frontend: {self.frontend_url}")
        
        print("\n📚 DOCUMENTATION:")
        print("   • Setup Guide: WEEK_2_3_SETUP_GUIDE.md")
        print("   • Status: WEEKS_2_3_COMPLETE.md")
        print("   • Quick Reference: QUICK_REFERENCE.md")
        
        print("\n🧪 TESTING:")
        print("   • Run tests: python backend/test_optimization.py")
        print("   • Week 2&3 tests: python backend/test_week2_week3.py")
        
        print("\n🌐 ACCESS:")
        print(f"   • Frontend: Open browser to {self.frontend_url}")
        print(f"   • Backend API: {self.backend_url}/docs")
        print(f"   • Health Check: {self.backend_url}/api/v1/intelligence/health")
        
        print("\n⚠️  TO STOP:")
        print("   • Press Ctrl+C in this terminal")
        print("   • Or run: taskkill /F /IM node.exe /IM python.exe")
        
        print("\n" + "="*80)
        print("🎉 SYSTEM READY!")
        print("="*80)
    
    def cleanup(self):
        """Cleanup processes on exit"""
        print("\n\n🛑 Shutting down...")
        for name, process in self.processes:
            try:
                print(f"   Stopping {name}...")
                process.terminate()
                process.wait(timeout=5)
            except:
                try:
                    process.kill()
                except:
                    pass
        print("✅ Cleanup complete")
    
    def run(self):
        """Run complete startup sequence"""
        try:
            # Check prerequisites
            if not self.check_prerequisites():
                print("\n❌ Prerequisites check failed")
                print("   Install missing tools and try again")
                return False
            
            # Check optional services
            self.check_optional_services()
            
            # Start backend
            if not self.start_backend():
                print("\n❌ Backend startup failed")
                return False
            
            # Verify backend
            if not self.verify_backend():
                print("\n❌ Backend verification failed")
                return False
            
            # Test API
            if not self.test_api_endpoint():
                print("\n❌ API test failed")
                return False
            
            # Start frontend
            if not self.start_frontend():
                print("\n❌ Frontend startup failed")
                return False
            
            # Verify frontend
            if not self.verify_frontend():
                print("\n❌ Frontend verification failed")
                return False
            
            # Print summary
            self.print_summary()
            
            # Keep running
            print("\n⏳ System is running. Press Ctrl+C to stop...")
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n\n⚠️  Received shutdown signal...")
            
            return True
        
        finally:
            self.cleanup()


def main():
    """Main entry point"""
    print("\n" + "="*80)
    print("🚀 MARKETSHIELD COMPLETE SYSTEM STARTUP")
    print("="*80)
    print("\nThis script will:")
    print("  1. Check prerequisites")
    print("  2. Check optional services (Redis, PostgreSQL, Celery)")
    print("  3. Start backend (FastAPI)")
    print("  4. Start frontend (React)")
    print("  5. Verify everything is working")
    print("\n" + "="*80)
    
    input("\nPress Enter to continue...")
    
    starter = SystemStarter()
    success = starter.run()
    
    if success:
        print("\n✅ System started successfully!")
        sys.exit(0)
    else:
        print("\n❌ System startup failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
