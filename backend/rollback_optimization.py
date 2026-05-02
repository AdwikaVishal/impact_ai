"""
Rollback Script for Backend Optimization
Safely disable new features if issues occur
"""
import os
from pathlib import Path


def update_env_file(disable_all=False):
    """Update .env file to disable features"""
    env_path = Path(__file__).parent / '.env'
    
    if not env_path.exists():
        print("❌ .env file not found")
        return False
    
    # Read current .env
    with open(env_path, 'r') as f:
        lines = f.readlines()
    
    # Update feature flags
    updated_lines = []
    for line in lines:
        if disable_all:
            # Disable all features
            if line.startswith('FEATURE_'):
                key = line.split('=')[0]
                updated_lines.append(f"{key}=false\n")
            else:
                updated_lines.append(line)
        else:
            # Just disable cache
            if line.startswith('FEATURE_CACHE_ENABLED'):
                updated_lines.append('FEATURE_CACHE_ENABLED=false\n')
            else:
                updated_lines.append(line)
    
    # Write updated .env
    with open(env_path, 'w') as f:
        f.writelines(updated_lines)
    
    return True


def rollback_cache_only():
    """Rollback cache features only"""
    print("\n" + "="*80)
    print("🔄 ROLLBACK: Disabling Cache Features")
    print("="*80)
    
    if update_env_file(disable_all=False):
        print("\n✅ Cache features disabled")
        print("\nChanges made:")
        print("  • FEATURE_CACHE_ENABLED=false")
        print("\nWhat this means:")
        print("  • System will use fresh API calls")
        print("  • No Redis dependency")
        print("  • Slower response times")
        print("  • Higher API costs")
        print("\nTo re-enable:")
        print("  • Set FEATURE_CACHE_ENABLED=true in backend/.env")
        print("  • Restart backend")
    else:
        print("\n❌ Rollback failed")


def rollback_all_features():
    """Rollback all optimization features"""
    print("\n" + "="*80)
    print("🔄 ROLLBACK: Disabling All Optimization Features")
    print("="*80)
    
    if update_env_file(disable_all=True):
        print("\n✅ All optimization features disabled")
        print("\nChanges made:")
        print("  • FEATURE_CACHE_ENABLED=false")
        print("  • FEATURE_CACHE_INTELLIGENCE=false")
        print("  • FEATURE_CACHE_PROFILES=false")
        print("  • FEATURE_CACHE_COMPETITORS=false")
        print("  • FEATURE_CACHE_DECISION_MAKERS=false")
        print("  • FEATURE_USE_PROSPEO=false")
        print("  • FEATURE_USE_APIFY=false")
        print("  • FEATURE_PARALLEL_PROCESSING=false")
        print("\nWhat this means:")
        print("  • System reverts to original behavior")
        print("  • Uses Hunter.io instead of Prospeo")
        print("  • Uses placeholder events instead of Apify")
        print("  • No caching")
        print("\nTo re-enable:")
        print("  • Set desired features to 'true' in backend/.env")
        print("  • Restart backend")
    else:
        print("\n❌ Rollback failed")


def show_current_status():
    """Show current feature flag status"""
    print("\n" + "="*80)
    print("📊 CURRENT FEATURE STATUS")
    print("="*80)
    
    env_path = Path(__file__).parent / '.env'
    
    if not env_path.exists():
        print("❌ .env file not found")
        return
    
    with open(env_path, 'r') as f:
        lines = f.readlines()
    
    print("\nFeature Flags:")
    for line in lines:
        if line.startswith('FEATURE_'):
            key, value = line.strip().split('=')
            enabled = value.lower() in ('true', '1', 'yes', 'on')
            status = "✅ ENABLED" if enabled else "❌ DISABLED"
            print(f"  {status}: {key}")


def main():
    """Main rollback menu"""
    print("\n" + "="*80)
    print("🔄 BACKEND OPTIMIZATION ROLLBACK TOOL")
    print("="*80)
    
    print("\nThis tool helps you safely disable optimization features if issues occur.")
    print("\nOptions:")
    print("  1. Show current feature status")
    print("  2. Disable cache only (keep new APIs)")
    print("  3. Disable all optimization features")
    print("  4. Exit")
    
    choice = input("\nEnter your choice (1-4): ").strip()
    
    if choice == '1':
        show_current_status()
    elif choice == '2':
        rollback_cache_only()
        print("\n⚠️  Remember to restart the backend for changes to take effect!")
    elif choice == '3':
        confirm = input("\n⚠️  This will disable ALL optimization features. Continue? (yes/no): ").strip().lower()
        if confirm == 'yes':
            rollback_all_features()
            print("\n⚠️  Remember to restart the backend for changes to take effect!")
        else:
            print("\n❌ Rollback cancelled")
    elif choice == '4':
        print("\n👋 Goodbye!")
    else:
        print("\n❌ Invalid choice")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Rollback cancelled")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
